{ buildPythonPackage, fetchFromGitHub, lib, ... }:

buildPythonPackage rec {
  pname = "kodistubs";
  version = "21.0.0";

  src = fetchFromGitHub {
    owner = "romanvm";
    repo = "Kodistubs";
    rev = "${version}";
    hash = "sha256-bkdSTwAmWLNLBr7figeOjqL+BZbw2dsyXMLzNSMYVLI=";
  };

  meta = with lib; {
    description = "(Former xbmcstubs) — stub Python functions and classes for Kodi mediacenter addon development";
    homepage = "https://github.com/romanvm/Kodistubs";
    license = licenses.gpl3;
    platforms = platforms.all;
    maintainers = with maintainers; [ kazenyuk ];
  };
}