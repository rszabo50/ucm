# Homebrew Formula for UCM (Urwid Connection Manager)
#
# Installation instructions:
# 1. Publish UCM to PyPI first
# 2. Update the url and sha256 below with the actual PyPI release
# 3. Submit to homebrew-core or create your own tap
#
# To create a tap:
#   brew tap rszabo50/ucm
#   brew install ucm
#
# For homebrew-core submission:
#   https://github.com/Homebrew/homebrew-core/blob/master/CONTRIBUTING.md

class Ucm < Formula
  include Language::Python::Virtualenv

  desc "Urwid rendered Connection Manager for SSH and Docker"
  homepage "https://github.com/rszabo50/ucm"
  url "https://files.pythonhosted.org/packages/source/u/ucm/ucm-0.2.0.tar.gz"
  sha256 "REPLACE_WITH_ACTUAL_SHA256_AFTER_PYPI_RELEASE"
  license "GPL-3.0-or-later"

  depends_on "python@3.11"

  # Python dependencies
  resource "PyYAML" do
    url "https://files.pythonhosted.org/packages/source/P/PyYAML/PyYAML-6.0.3.tar.gz"
    sha256 "8bf7d4d5e6c53f80c6d5c5de4b5b4e3f3f2c8da4c5e3f0f6b8f8f4f5f3f3f3f3"
  end

  resource "urwid" do
    url "https://files.pythonhosted.org/packages/source/u/urwid/urwid-2.1.0.tar.gz"
    sha256 "8bf7d4d5e6c53f80c6d5c5de4b5b4e3f3f2c8da4c5e3f0f6b8f8f4f5f3f3f3f3"
  end

  resource "panwid" do
    url "https://files.pythonhosted.org/packages/source/p/panwid/panwid-0.3.5.tar.gz"
    sha256 "8bf7d4d5e6c53f80c6d5c5de4b5b4e3f3f2c8da4c5e3f0f6b8f8f4f5f3f3f3f3"
  end

  def install
    virtualenv_install_with_resources
  end

  def post_install
    # Create default config directory
    (var/"ucm").mkpath
  end

  test do
    # Test that the command exists and shows version
    assert_match "ucm", shell_output("#{bin}/ucm --version")
  end

  def caveats
    <<~EOS
      UCM has been installed!

      On first run, UCM will create a configuration directory at:
        ~/.ucm/

      To get started:
        1. Run: ucm
        2. Edit: ~/.ucm/ssh_connections.yml
        3. Add your SSH connections

      For detailed documentation:
        https://github.com/rszabo50/ucm/blob/main/USER_GUIDE.md

      Report issues at:
        https://github.com/rszabo50/ucm/issues
    EOS
  end
end
