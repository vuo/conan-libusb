from conans import ConanFile

class LibusbTestConan(ConanFile):
    generators = 'qbs'

    def build(self):
        self.run('qbs -f "%s"' % self.source_folder)

    def imports(self):
        self.copy('*.dylib', dst='bin', src='lib')

    def test(self):
        self.run('qbs run')

        # Ensure we only link to system libraries.
        self.run('! (otool -L bin/libusb.dylib | tail +3 | egrep -v "^\s*(/usr/lib/|/System/)")')
