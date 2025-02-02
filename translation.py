import argostranslate.package
import argostranslate.translate

from_code = "fr"
to_code = "en"

# Download and install Argos Translate package
argostranslate.package.update_package_index()
available_packages = argostranslate.package.get_available_packages()
package_to_install = next(
    filter(
        lambda x: x.from_code == from_code and x.to_code == to_code, available_packages
    )
)
argostranslate.package.install_from_path(package_to_install.download())

def translate(text):
    return argostranslate.translate.translate(text, from_code, to_code)
