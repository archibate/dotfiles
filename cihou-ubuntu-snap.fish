#!/usr/bin/env fish

echo '#!/usr/bin/bash

if [ -t 1 ]; then
    exec -a "$0" /usr/bin/snap "$@"
else
    exec -a "$0" /usr/bin/snap "$@" | cat
fi
' > ~/.local/bin/snap

chmod +x ~/.local/bin/snap

# for x in (ls /snap/bin/); if string match "/snap/bin/*" (which $x); and string match "/usr/bin/snap" (readlink (which $x)); echo linking $x; ln -s snap ~/.local/bin/$x; end; end
for x in (ls /snap/bin/); if string match "/snap/bin/*" (which $x); echo linking $x; ln -s snap ~/.local/bin/$x; end; end
