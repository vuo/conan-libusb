from conans import ConanFile, tools, AutoToolsBuildEnvironment
import shutil
import os

class LibusbConan(ConanFile):
    name = 'libusb'

    source_version = '1.0.21'
    package_version = '3'
    version = '%s-%s' % (source_version, package_version)

    settings = 'os', 'compiler', 'build_type', 'arch'
    url = 'https://github.com/vuo/conan-libusb'
    license = 'https://github.com/libusb/libusb/blob/master/COPYING'
    description = 'A library for USB device access'
    source_dir = 'libusb-%s' % source_version
    build_dir = '_build'

    def source(self):
        tools.get('https://github.com/libusb/libusb/releases/download/v%s/libusb-%s.tar.bz2' % (self.source_version, self.source_version),
                  sha256='7dce9cce9a81194b7065ee912bcd55eeffebab694ea403ffb91b67db66b1824b')

    def build(self):
        tools.mkdir(self.build_dir)
        with tools.chdir(self.build_dir):
            autotools = AutoToolsBuildEnvironment(self)
            autotools.flags.append('-Oz')
            autotools.flags.append('-mmacosx-version-min=10.10')
            autotools.link_flags.append('-Wl,-install_name,@rpath/libusb.dylib')
            autotools.configure(configure_dir='../%s' % self.source_dir,
                                args=['--quiet',
                                      '--enable-shared',
                                      '--disable-static',
                                      '--prefix=%s' % os.getcwd()])
            autotools.make(args=['install'])
            # libusb calls itself 1.0.0 regardless of the actual release version.
            shutil.move('lib/libusb-1.0.0.dylib', 'lib/libusb.dylib')

    def package(self):
        self.copy('*.h', src='%s/include' % self.build_dir, dst='include')
        self.copy('libusb.dylib', src='%s/lib' % self.build_dir, dst='lib')

    def package_info(self):
        self.cpp_info.libs = ['usb']
