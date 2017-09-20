from conans import ConanFile, tools, AutoToolsBuildEnvironment
import os

class LibusbConan(ConanFile):
    name = 'libusb'
    version = '1.0.21'
    settings = 'os', 'compiler', 'build_type', 'arch'
    url = 'http://libusb.info/' # @@@ should be url to package
    license = 'https://github.com/libusb/libusb/blob/master/COPYING'
    description = 'A library for USB device access'
    source_dir = 'libusb-%s' % version
    build_dir = '_build'
    # libusb calls itself 1.0.0 regardless of the actual release version.
    dylib_name = 'libusb-1.0.0.dylib'

    def source(self):
        tools.get('https://github.com/libusb/libusb/releases/download/v%s/libusb-%s.tar.bz2' % (self.version, self.version),
                  # sha256='7dce9cce9a81194b7065ee912bcd55eeffebab694ea403ffb91b67db66b1824b'
                  )

    def build(self):
        tools.mkdir(self.build_dir)
        with tools.chdir(self.build_dir):
            autotools = AutoToolsBuildEnvironment(self)
            autotools.cxx_flags.append('-Oz')
            autotools.cxx_flags.append('-mmacosx-version-min=10.8')
            autotools.link_flags.append('-Wl,-install_name,@rpath/%s' % self.dylib_name)
            autotools.configure(configure_dir='../%s' % self.source_dir,
                                args=['--quiet',
                                      '--enable-shared',
                                      '--disable-static',
                                      '--prefix=%s' % os.getcwd()])
            autotools.make(args=['install'])

    def package(self):
        self.copy('*.h', src='%s/include' % self.build_dir, dst='include')
        self.copy(self.dylib_name, src='%s/lib' % self.build_dir, dst='lib')

    def package_info(self):
        self.cpp_info.libs = ['usb-1.0.0']
