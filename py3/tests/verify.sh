#!/bin/bash -i
#

# Safety check: must run from a directory named "tests"
if [[ "$(basename "$PWD")" != "tests" ]]; then
    echo "ERROR: verify.sh must be run from a directory named 'tests'." >&2
    echo "  Current PWD: $PWD" >&2
    exit 1
fi

# Starting-point smoke test for bisos.prometheus -- covers prometheusAdmin.cs, quickPrometheus.cs,
# the read-only Cmnds of the planted files, and bisos.prometheus.prometheusInfo's generators.
# Nothing here installs, starts or writes anything on the host.

# --- CS entry points: smoke test (no args → examples/usage, non-zero ok) ---

lpDo ../bin/prometheusAdmin.cs
lpDo ../bin/quickPrometheus.cs
lpDo ../bin/prometheus-assemble.cs

# --- prometheusAdmin.cs: each admin sub-Cmnd runs and produces examples output ---

lpDo ../bin/prometheusAdmin.cs -i examples
lpDo ../bin/prometheusAdmin.cs -i hostInfo
lpDo ../bin/prometheusAdmin.cs -i servicesInfo
lpDo ../bin/prometheusAdmin.cs -i queriesInfo
lpDo ../bin/prometheusAdmin.cs -i driftCheck
lpDo ../bin/prometheusAdmin.cs -i fullUpdate

# --- planted files: menus and read-only Cmnds ---

lpDo ../bin/prometheus-sbom.pcs -i readme
lpDo ../bin/prometheusUsage-sbom.pcs -i readme
lpDo ../bin/prometheusCbs-sbom.pcs -i readme
lpDo ../bin/prometheus-sysd.pcs
lpDo ../bin/prometheus-node-exporter-sysd.pcs
lpDo ../bin/prometheus-cbs.pcs
lpDo ../bin/cbmProc-prometheus.spcs
lpDo ../bin/prometheus-here-dns.pcs
lpDo ../bin/prometheus-wvd.pcs -i configFileStdout --cls=configFile_nginxVd

# --- bisos.prometheus.prometheusInfo: banna numbers and generator invariants ---

lpDo python3 -c "
import subprocess, sys
from bisos.banna import sysAccts
from bisos.prometheus.prometheusInfo import (
    prometheusInfo as i, configFileContent, envFileContent, nodeExporterEnvFileContent,
    promDistSetupScript, nodeExporterSetupScript, kvDrift, textDrift,
)

cases = [
    ('banna: prometheus port',          i.portNu == 24010),
    ('banna: node_exporter port',       i.nodeExporterPortNu == 24012),
    ('banna sysAccts: prometheus uid',  sysAccts.sysAcctOf(i.acctName).uid == 504),
    ('banna sysAccts: homeDir',         sysAccts.sysAcctOf(i.acctName).homeDir == str(i.dataDir.parent)),
    ('server on loopback',              f'--web.listen-address=127.0.0.1:{i.portNu}' in envFileContent()),
    ('links point at prometheus.here',  '--web.external-url=http://prometheus.here/' in envFileContent()),
    ('exporter on loopback',            f'127.0.0.1:{i.nodeExporterPortNu}' in nodeExporterEnvFileContent()),
    ('scrapes itself and the exporter', i.listenAddr in configFileContent() and i.nodeExporterAddr in configFileContent()),
    ('tarball scripts parse',           all(subprocess.run(['bash', '-n'], input=s, text=True).returncode == 0
                                            for s in (promDistSetupScript(), nodeExporterSetupScript()))),
    ('amd64 checksum pinned',           dict(i.distSha256).get('amd64', '') != ''),
    ('drift: identical is clean',       kvDrift(envFileContent(), envFileContent()) == {'missing': [], 'differs': [], 'extra': []}),
    ('drift: yaml edit reported',       textDrift(configFileContent() + '# x\n', configFileContent()) != []),
]

failed = 0
for name, ok in cases:
    print(f'  [{\"PASS\" if ok else \"FAIL\"}] {name}')
    failed += not ok

if failed:
    print(f'prometheusInfo: {failed} test(s) FAILED')
    sys.exit(1)
else:
    print('prometheusInfo: all cases PASS')
" 2>/dev/null || true
