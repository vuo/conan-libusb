from conans import ConanFile, tools, AutoToolsBuildEnvironment
import shutil
import os
import platform

class LibusbConan(ConanFile):
    name = 'libusb'

    source_version = '1.0.21'
    package_version = '3'
    version = '%s-%s' % (source_version, package_version)

    build_requires = 'llvm/3.3-5@vuo/stable'
    settings = 'os', 'compiler', 'build_type', 'arch'
    url = 'https://github.com/vuo/conan-libusb'
    license = 'https://github.com/libusb/libusb/blob/master/COPYING'
    description = 'A library for USB device access'
    source_dir = 'libusb-%s' % source_version
    build_dir = '_build'

    def requirements(self):
        if platform.system() == 'Linux':
            self.requires('patchelf/0.10pre-1@vuo/stable')
        elif platform.system() != 'Darwin':
            raise Exception('Unknown platform "%s"' % platform.system())

    def source(self):
        tools.get('https://github.com/libusb/libusb/releases/download/v%s/libusb-%s.tar.bz2' % (self.source_version, self.source_version),
                  sha256='7dce9cce9a81194b7065ee912bcd55eeffebab694ea403ffb91b67db66b1824b')

        self.run('mv %s/COPYING %s/%s.txt' % (self.source_dir, self.source_dir, self.name))

    def build(self):
        tools.mkdir(self.build_dir)
        with tools.chdir(self.build_dir):
            autotools = AutoToolsBuildEnvironment(self)

            # The LLVM/Clang libs get automatically added by the `requires` line,
            # but this package doesn't need to link with them.
            autotools.libs = ['c++abi']

            autotools.flags.append('-Oz')

            if platform.system() == 'Darwin':
                autotools.flags.append('-mmacosx-version-min=10.10')
                autotools.link_flags.append('-Wl,-install_name,@rpath/libusb.dylib')

            env_vars = {
                'CC' : self.deps_cpp_info['llvm'].rootpath + '/bin/clang',
                'CXX': self.deps_cpp_info['llvm'].rootpath + '/bin/clang++',
            }
            with tools.environment_append(env_vars):
                autotools.configure(configure_dir='../%s' % self.source_dir,
                                    args=['--quiet',
                                          '--enable-shared',
                                          '--disable-static',
                                          '--prefix=%s' % os.getcwd()])
                autotools.make(args=['install'])
                # libusb calls itself 1.0.0 regardless of the actual release version.
                if platform.system() == 'Darwin':
                    shutil.move('lib/libusb-1.0.0.dylib', 'lib/libusb.dylib')
                elif platform.system() == 'Linux':
                    shutil.move('lib/libusb-1.0.so.0.1.0', 'lib/libusb.so')
                    patchelf = self.deps_cpp_info['patchelf'].rootpath + '/bin/patchelf'
                    self.run('%s --set-soname libusb.so lib/libusb.so' % patchelf)

    def package(self):
        if platform.system() == 'Darwin':
            libext = 'dylib'
        elif platform.system() == 'Linux':
            libext = 'so'
        else:
            raise Exception('Unknown platform "%s"' % platform.system())

        self.copy('*.h', src='%s/include' % self.build_dir, dst='include')
        self.copy('libusb.%s' % libext, src='%s/lib' % self.build_dir, dst='lib')

        self.copy('%s.txt' % self.name, src=self.source_dir, dst='license')

    def package_info(self):
        self.cpp_info.libs = ['usb']
