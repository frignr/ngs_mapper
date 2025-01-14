from imports import *
from ngs_mapper import compat

class Base(common.BaseBaseCaller):
    modulepath = 'ngs_mapper.vcf_diff'

    def setUp( self ):
        super(Base,self).setUp()
        fixpath = join(fixtures.THIS,'fixtures')
        
        # Bam built from scratch that has multiple refs
        self.test_vcf = self.vcf
        self.test_vcf_diff = join(fixpath,'vcf_diff','test.vcf.diff')
        self.fixture1 = (self.test_vcf,self.test_vcf_diff)

        # Single reference vcf with lots of bases
        self.full_vcf = join(fixpath,'base_caller','fullsample','fullsample.bam.vcf')
        self.full_vcf_diff = join(fixpath,'vcf_diff','fullsample.vcf.diff')
        self.fixture2 = (self.full_vcf,self.full_vcf_diff)

    def run_fixture( self, vcf, diff_file ):
        output = self.run_vcf_diff( vcf )
        with open(diff_file) as fh:
            eq_( fh.read(), output, "Output did not match expected output from file {0}".format(diff_file) )

    def run_vcf_diff( self, vcffile, *args, **kwargs ):
        import subprocess
        script = 'vcf_diff'

        cmd = [script,vcffile]
        print "Running {0}".format(' '.join(cmd))
        try:
            return compat.check_output( cmd, stderr=subprocess.STDOUT )
        except subprocess.CalledProcessError as e:
            return e.output

class TestFunctional(Base):
    def test_fixtures( self ):
        self.run_fixture( *self.fixture1 )
        self.run_fixture( *self.fixture2 )
