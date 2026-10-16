# -*- coding: utf-8 -*-

""" #+begin_org
* ~[Summary]~ :: =CS-Lib= The single source of the facts of this host's Prometheus (and node_exporter) installation.
#+end_org """

""" #+begin_org
* [[elisp:(org-cycle)][| ~Description~ |]] :: Facts shared by prometheus-sbom.pcs, prometheusUsage-sbom.pcs,
prometheusAdmin.cs, quickPrometheus.cs, prometheus-sysd.pcs, prometheus-node-exporter-sysd.pcs,
prometheus-here-dns.pcs and prometheus-wvd.pcs: the account, the pinned upstream versions and their
checksums, the install/config/data paths, the EnvironmentFiles, the fqdn and the two banna ports.
** Pure: importing this module has no side effects and touches no host state.
** The generators below return the text of /etc/prometheus/prometheus.yml, /etc/default/prometheus,
/etc/default/prometheus-node-exporter and of the shared [Service] lines of the units, so that the code
that writes them and the code that checks them (prometheusAdmin.cs -i driftCheck) cannot disagree.
** Status: Starting point.
** /[[elisp:(org-cycle)][| Planned Improvements |]]/ :
*** TODO A login in front of prometheus.here (Prometheus has none; it listens on loopback only).
*** TODO Architectures other than amd64: add each one's checksum to the *Sha256 dicts.
#+end_org """

####+BEGIN: b:prog:file/proclamations :outLevel 1
""" #+begin_org
* *[[elisp:(org-cycle)][| Proclamations |]]* :: Libre-Halaal Software --- Part Of BISOS ---  Poly-COMEEGA Format.
** This is Libre-Halaal Software. © Neda Communications, Inc. Subject to AGPL.
** It is part of BISOS (ByStar Internet Services OS)
** Best read and edited  with Blee in Poly-COMEEGA (Polymode Colaborative Org-Mode Enhance Emacs Generalized Authorship)
#+end_org """
####+END:

####+BEGIN: b:prog:file/particulars :authors ("./inserts/authors-mb.org")
""" #+begin_org
* *[[elisp:(org-cycle)][| Particulars |]]* :: Authors, version
** This File: /bisos/git/bxRepos/bisos-pip/prometheus/py3/bisos/prometheus/prometheusInfo.py
** Authors: Mohsen BANAN, http://mohsen.banan.1.byname.net/contact
#+end_org """
####+END:

import dataclasses
import difflib
import pathlib

from bisos.banna import tcpPorts as bannaTcpPorts


def _bannaPortNu(portName: str) -> int:
    """The registry, bisos.banna, is authoritative: never hardcode these ports."""
    return bannaTcpPorts.tcpPortsAssignedList.tcpPortsList[portName].portNu


@dataclasses.dataclass(frozen=True)
class PrometheusInfo:
    """The facts of this host's Prometheus installation. Built once, as prometheusInfo below."""

    # The OS account both units run as (node_exporter too, as Debian's package does).
    acctName: str = "prometheus"

    # Upstream release tarballs, pinned with the SHA-256 each release publishes in its
    # sha256sums.txt. Debian packages Prometheus, but trixie's is 2.x; upstream is 3.x.
    # Checksums are per Debian architecture; an architecture with no entry is refused.
    version: str = "3.15.0"
    distSha256: tuple = (("amd64", "2a542df32eac02ee17b9d844fb2aa1de00dafa5476579ba8a3ba862e9d572ea0"),)

    nodeExporterVersion: str = "1.12.1"
    nodeExporterSha256: tuple = (("amd64", "b51d8a76aa2a9156a55d501aca6276fae09e262259a5e4e831d2c2222f084e63"),)

    # Binaries: root-owned, read-only for the account. One dir per version, plus a link,
    # so an upgrade is unpack + flip and a rollback is a flip.
    installBase: pathlib.Path = pathlib.Path("/opt/prometheus")

    confDir: pathlib.Path = pathlib.Path("/etc/prometheus")

    # The TSDB. Owned by the account.
    dataDir: pathlib.Path = pathlib.Path("/var/lib/prometheus/data")

    # Read by systemd as root before the units drop to User=. root:acctName 640.
    envFile: pathlib.Path = pathlib.Path("/etc/default/prometheus")
    nodeExporterEnvFile: pathlib.Path = pathlib.Path("/etc/default/prometheus-node-exporter")

    # Every listener binds loopback only: Prometheus and node_exporter have no authentication.
    # nginx (prometheus.here) reaches Prometheus over loopback.
    listenIp: str = "127.0.0.1"

    retentionTime: str = "15d"
    scrapeInterval: str = "15s"

    fqdn: str = "prometheus.here"

    portNu: int = dataclasses.field(default_factory=lambda: _bannaPortNu('prometheus'))
    nodeExporterPortNu: int = dataclasses.field(default_factory=lambda: _bannaPortNu('prometheusNodeExporter'))

    def distName(self, arch: str = "amd64") -> str:
        return f"prometheus-{self.version}.linux-{arch}"

    def distUrl(self, arch: str = "amd64") -> str:
        return (f"https://github.com/prometheus/prometheus/releases/download/"
                f"v{self.version}/{self.distName(arch)}.tar.gz")

    def distDir(self, arch: str = "amd64") -> pathlib.Path:
        return self.installBase / self.distName(arch)

    @property
    def homeLink(self) -> pathlib.Path:
        """installBase/current -> distDir. Units and CLI go through this, never through distDir."""
        return self.installBase / "current"

    @property
    def promBin(self) -> pathlib.Path:
        return self.homeLink / "prometheus"

    @property
    def promtool(self) -> pathlib.Path:
        return self.homeLink / "promtool"

    def nodeExporterDistName(self, arch: str = "amd64") -> str:
        return f"node_exporter-{self.nodeExporterVersion}.linux-{arch}"

    def nodeExporterUrl(self, arch: str = "amd64") -> str:
        return (f"https://github.com/prometheus/node_exporter/releases/download/"
                f"v{self.nodeExporterVersion}/{self.nodeExporterDistName(arch)}.tar.gz")

    def nodeExporterDir(self, arch: str = "amd64") -> pathlib.Path:
        return self.installBase / self.nodeExporterDistName(arch)

    @property
    def nodeExporterLink(self) -> pathlib.Path:
        return self.installBase / "node_exporter"

    @property
    def nodeExporterBin(self) -> pathlib.Path:
        return self.nodeExporterLink / "node_exporter"

    @property
    def configFile(self) -> pathlib.Path:
        return self.confDir / "prometheus.yml"

    @property
    def listenAddr(self) -> str:
        return f"{self.listenIp}:{self.portNu}"

    @property
    def nodeExporterAddr(self) -> str:
        return f"{self.listenIp}:{self.nodeExporterPortNu}"

    @property
    def baseUrl(self) -> str:
        """The address humans browse, through the nginx vhost."""
        return f"http://{self.fqdn}"

    @property
    def localUrl(self) -> str:
        """Straight to Prometheus, bypassing nginx. What Grafana and promtool use."""
        return f"http://{self.listenAddr}"


# A Singleton
prometheusInfo = PrometheusInfo()


def tarballSetupScript(url: str, sha256: tuple, dirName: str, link: pathlib.Path,
                       base: pathlib.Path, hasTopDir: bool = True) -> str:
    """Bash: fetch a pinned release tarball for this host's architecture, verify, unpack, link.

    Unpacked once per version into base/<dirName>, root-owned; link then points at it. A tarball
    whose SHA-256 does not match is discarded and nothing is unpacked. url and dirName may contain
    the literal ARCH, replaced by the Debian architecture at run time. hasTopDir=False is for
    tarballs whose files are at the top level (gcx): they are unpacked into base/<dirName>.
    """
    cases = "\n".join(f'    {arch}) sha={sha} ;;' for arch, sha in sha256)
    into = "{base}" if hasTopDir else '"$dir"'
    return f"""
set -e
arch=$(dpkg --print-architecture)
case "$arch" in
{cases}
    *) echo "no pinned checksum for architecture $arch" >&2 ; exit 1 ;;
esac
dir={base}/{dirName.replace("ARCH", "$arch")}
sudo mkdir -p {base}
if [ ! -d "$dir" ] ; then
    tmpDir=$(mktemp -d)
    trap 'rm -rf "$tmpDir"' EXIT
    curl -fsSL -o "$tmpDir/dist.tgz" {url.replace("ARCH", "$arch")}
    echo "$sha  $tmpDir/dist.tgz" | sha256sum -c --quiet -
    {"" if hasTopDir else 'sudo mkdir -p "$dir"'}
    sudo tar -xzf "$tmpDir/dist.tgz" -C {into.format(base=base)}
    sudo chown -R root:root "$dir"
fi
sudo ln -sfn "$dir" {link}
"""


def promDistSetupScript(info: PrometheusInfo = prometheusInfo) -> str:
    """The Prometheus tarball (prometheus and promtool). Used by both the server and the usage sbom."""
    return tarballSetupScript(info.distUrl("ARCH"), info.distSha256, info.distName("ARCH"),
                              info.homeLink, info.installBase)


def nodeExporterSetupScript(info: PrometheusInfo = prometheusInfo) -> str:
    return tarballSetupScript(info.nodeExporterUrl("ARCH"), info.nodeExporterSha256,
                              info.nodeExporterDistName("ARCH"), info.nodeExporterLink, info.installBase)


def configFileContent(info: PrometheusInfo = prometheusInfo) -> str:
    """The content /etc/prometheus/prometheus.yml is generated with. Written only when absent.

    Two scrape jobs: Prometheus itself and this host's node_exporter. Both are on loopback.
    """
    return (
        "# Generated by prometheus-sbom.pcs from bisos.prometheus.prometheusInfo. Written only when absent.\n"
        "global:\n"
        f"  scrape_interval: {info.scrapeInterval}\n"
        f"  evaluation_interval: {info.scrapeInterval}\n"
        "\n"
        "scrape_configs:\n"
        "  - job_name: prometheus\n"
        "    static_configs:\n"
        f"      - targets: ['{info.listenAddr}']\n"
        "  - job_name: node\n"
        "    static_configs:\n"
        f"      - targets: ['{info.nodeExporterAddr}']\n"
    )


def envFileContent(info: PrometheusInfo = prometheusInfo) -> str:
    """The content /etc/default/prometheus is generated with. Written only when absent.

    ARGS is expanded by the unit's ExecStart as separate words ($ARGS, not ${ARGS}).
    --web.external-url makes the links Prometheus renders point at prometheus.here.
    """
    return (
        f'ARGS="--config.file={info.configFile} --storage.tsdb.path={info.dataDir}'
        f' --storage.tsdb.retention.time={info.retentionTime}'
        f' --web.listen-address={info.listenAddr} --web.external-url={info.baseUrl}/"\n'
        "# Add flags (e.g. --web.enable-lifecycle) to ARGS above\n"
    )


def nodeExporterEnvFileContent(info: PrometheusInfo = prometheusInfo) -> str:
    """The content /etc/default/prometheus-node-exporter is generated with. Written only when absent."""
    return (
        f'ARGS="--web.listen-address={info.nodeExporterAddr}"\n'
        "# Add collector flags (e.g. --collector.systemd) to ARGS above\n"
    )


def sysdServiceLines(envFile: pathlib.Path, info: PrometheusInfo = prometheusInfo) -> str:
    """The identity lines every prometheus unit has in its [Service] section."""
    return (
        f"User={info.acctName}\n"
        f"Group={info.acctName}\n"
        f"EnvironmentFile={envFile}\n"
    )


def _kvMap(text: str) -> dict[str, str]:
    """KEY=VALUE lines of an EnvironmentFile; comments and blank lines are skipped."""
    pairs: dict[str, str] = {}
    for line in text.splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, _, value = line.partition("=")
        pairs[key.strip()] = value.strip()
    return pairs


def kvDrift(liveText: str, generatedText: str) -> dict[str, list]:
    """Compare a live KEY=VALUE file with what its generator would produce.

    The files are written only when absent, so hand overrides are legitimate. Reports:
      missing -- keys the generator has and the live file lacks
      differs -- (key, expected, live) where both have the key with different values
      extra   -- keys only the live file has (hand additions)
    """
    expected = _kvMap(generatedText)
    live = _kvMap(liveText)
    return {
        "missing": [k for k in expected if k not in live],
        "differs": [(k, expected[k], live[k]) for k in expected if k in live and live[k] != expected[k]],
        "extra": [k for k in live if k not in expected],
    }


def textDrift(liveText: str, generatedText: str) -> list[str]:
    """A unified diff of a structured file (YAML) against its generator; empty when they agree."""
    return list(difflib.unified_diff(generatedText.splitlines(), liveText.splitlines(),
                                     "generator", "live", lineterm=""))


def unitDrift(unitText: str, envFile: pathlib.Path, info: PrometheusInfo = prometheusInfo) -> list[str]:
    """The identity lines (sysdServiceLines) that an installed unit file lacks."""
    present = {line.strip() for line in unitText.splitlines()}
    return [line for line in sysdServiceLines(envFile, info).splitlines() if line not in present]


####+BEGIN: b:py3:cs:framework/endOfFile :basedOn "classification"
""" #+begin_org
* [[elisp:(org-cycle)][| *End-Of-Editable-Text* |]] :: emacs and org variables and control parameters
#+end_org """

#+STARTUP: showall

### local variables:
### no-byte-compile: t
### end:
####+END:
