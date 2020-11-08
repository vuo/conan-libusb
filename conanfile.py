from conans import ConanFile, tools, AutoToolsBuildEnvironment
import shutil
import os
import platform

class LibusbConan(ConanFile):
    name = 'libusb'

    source_version = '1.0.23'
    package_version = '0'
    version = '%s-%s' % (source_version, package_version)

    build_requires = (
        'llvm/5.0.2-1@vuo/stable',
        'macos-sdk/11.0-0@vuo/stable',
    )
    settings = 'os', 'compiler', 'build_type', 'arch'
    url = 'https://github.com/libusb/libusb'
    license = 'https://github.com/libusb/libusb/blob/master/COPYING'
    description = 'A library for USB device access'
    source_dir = 'libusb-%s' % source_version

    build_x86_dir = '_build_x86'
    build_arm_dir = '_build_arm'
    install_x86_dir = '_install_x86'
    install_arm_dir = '_install_arm'
    install_universal_dir = '_install_universal_dir'

    def requirements(self):
        if platform.system() == 'Linux':
            self.requires('patchelf/0.10pre-1@vuo/stable')
        elif platform.system() != 'Darwin':
            raise Exception('Unknown platform "%s"' % platform.system())

    def source(self):
        tools.get('https://github.com/libusb/libusb/releases/download/v%s/libusb-%s.tar.bz2' % (self.source_version, self.source_version),
                  sha256='db11c06e958a82dac52cf3c65cb4dd2c3f339c8a988665110e0d24d19312ad8d')

        self.run('mv %s/COPYING %s/%s.txt' % (self.source_dir, self.source_dir, self.name))

    def build(self):
        autotools = AutoToolsBuildEnvironment(self)

        # The LLVM/Clang libs get automatically added by the `requires` line,
        # but this package doesn't need to link with them.
        autotools.libs = []

        autotools.flags.append('-Oz')

        if platform.system() == 'Darwin':
            autotools.flags.append('-isysroot %s' % self.deps_cpp_info['macos-sdk'].rootpath)
            autotools.flags.append('-mmacosx-version-min=10.11')
            autotools.link_flags.append('-Wl,-install_name,@rpath/libusb.dylib')

        common_configure_args = [
            '--quiet',
            '--disable-dependency-tracking',
            '--disable-static',
            '--enable-shared',
        ]

        env_vars = {
            'CC' : self.deps_cpp_info['llvm'].rootpath + '/bin/clang',
            'CXX': self.deps_cpp_info['llvm'].rootpath + '/bin/clang++',
        }
        with tools.environment_append(env_vars):
            build_root = os.getcwd()

            self.output.info("=== Build for x86_64 ===")
            tools.mkdir(self.build_x86_dir)
            with tools.chdir(self.build_x86_dir):
                autotools.flags.append('-arch x86_64')
                autotools.link_flags.append('-arch x86_64')
                autotools.configure(configure_dir='../%s' % self.source_dir,
                                    build=False,
                                    host=False,
                                    args=common_configure_args + [
                                        '--prefix=%s/%s' % (build_root, self.install_x86_dir),
                                    ])
                autotools.make(args=['--quiet'])
                autotools.make(target='install', args=['--quiet'])

            self.output.info("=== Build for arm64 ===")
            tools.mkdir(self.build_arm_dir)
            with tools.chdir(self.build_arm_dir):
                autotools.flags.remove('-arch x86_64')
                autotools.flags.append('-arch arm64')
                autotools.link_flags.remove('-arch x86_64')
                autotools.link_flags.append('-arch arm64')
                autotools.configure(configure_dir='../%s' % self.source_dir,
                                    build=False,
                                    host=False,
                                    args=common_configure_args + [
                                        '--prefix=%s/%s' % (build_root, self.install_arm_dir),
                                        '--host=x86_64-apple-darwin15.0.0',
                                    ])
                autotools.make(args=['--quiet'])
                autotools.make(target='install', args=['--quiet'])

    def package(self):
        if platform.system() == 'Darwin':
            libext = 'dylib'
        elif platform.system() == 'Linux':
            libext = 'so'
        else:
            raise Exception('Unknown platform "%s"' % platform.system())

        tools.mkdir(self.install_universal_dir)
        with tools.chdir(self.install_universal_dir):
            self.run('lipo -create ../%s/lib/libusb-1.0.%s ../%s/lib/libusb-1.0.%s -output libusb.%s' % (self.install_x86_dir, libext, self.install_arm_dir, libext, libext))

        self.copy('*.h', src='%s/include' % self.install_x86_dir, dst='include')
        self.copy('libusb.%s' % libext, src=self.install_universal_dir, dst='lib')

        self.copy('%s.txt' % self.name, src=self.source_dir, dst='license')

    def package_info(self):
        self.cpp_info.libs = ['usb']
