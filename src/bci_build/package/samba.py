"""Samba container definition"""

import textwrap

from pathlib import Path

from bci_build.container_attributes import TCP
from bci_build.container_attributes import SupportLevel
from bci_build.os_version import CAN_BE_LATEST_OS_VERSION
from bci_build.package import DOCKERFILE_RUN
from bci_build.package import ApplicationStackContainer
from bci_build.package import OsContainer
from bci_build.package import OsVersion
from bci_build.package import ParseVersion
from bci_build.package import Replacement
from bci_build.package import _build_tag_prefix
from bci_build.package.helpers import generate_package_version_check
from bci_build.package.versions import format_version
from bci_build.package.versions import get_pkg_version

SAMBA_SERVER_CONTAINERS = []
SAMBA_CLIENT_CONTAINERS = []
SAMBA_TOOLBOX_CONTAINERS = []


for os_version in (OsVersion.TUMBLEWEED, OsVersion.SP6, OsVersion.SP7):
    srv = ApplicationStackContainer(
        name="samba-server",
        pretty_name="Samba Server",
        custom_description=(
            "Samba is a feature-rich Open Source implementation of the SMB and "
            "Active Directory protocols for Linux and UNIX-like systems.\n\n"
            "Samba is a high-performance, scalable distributed software "
            "for providing access to various cluster filesystems. "
            "It enables cloud platform-as-a-service (PaaS) providers, "
            "software-defined storage (SDS) solutions, high-performance "
            "computing (HPC) applications, and enterprise-grade network "
            "attached storage (NAS) to support the latest security and "
            "SMB capabilities.\n\n"
            "This image is {based_on_container}."
        ),
        from_target_image=f"{_build_tag_prefix(os_version)}/bci-micro:{OsContainer.version_to_container_os_version(os_version)}",
        os_version=os_version,
        is_latest=os_version in CAN_BE_LATEST_OS_VERSION,
        is_singleton_image=True,
        version="%%samba_version%%",
        version_in_uid=False,
        support_level=SupportLevel.L3,
        tag_version=format_version(
            samba_version := get_pkg_version("samba", os_version), ParseVersion.MINOR
        ),
        additional_versions=[format_version(samba_version, ParseVersion.MAJOR)],
        build_stage_custom_end=generate_package_version_check(
            "samba", samba_version, ParseVersion.MINOR, use_target=True
        ),
        replacements_via_service=[
            Replacement(
                regex_in_build_description="%%samba_version%%", package_name="samba"
            )
        ],
        license="GPL-3.0-or-later",
        package_list=[
            "catatonit",
            "samba",
            # "ctdb",
            # "timezone",
        ],
        extra_files={
            "docker-entrypoint.sh": (Path(__file__).parent / "samba-server" / "entrypoint.sh").read_bytes(),
            "smbuser.sh": (Path(__file__).parent / "samba-server" / "smbuser.sh").read_bytes(),
            "shadow.sh": (Path(__file__).parent / "samba-server" / "shadow.sh").read_bytes(),
            "smb.conf": (Path(__file__).parent / "samba-server" / "smb.conf").read_bytes(),
        },
        entrypoint=["/usr/local/bin/docker-entrypoint.sh"],
        exposes_ports=[TCP(445)],
        volumes=["/shares", "/var/lib/samba"],
        custom_end=textwrap.dedent(f"""
            COPY smb.conf /etc/samba/

            COPY docker-entrypoint.sh /usr/local/bin/
            {DOCKERFILE_RUN} chmod 755 /usr/local/bin/docker-entrypoint.sh

            COPY smbuser.sh /usr/local/bin/smbuser
            {DOCKERFILE_RUN} chmod 755 /usr/local/bin/smbuser

            COPY shadow.sh /usr/local/bin/useradd
            {DOCKERFILE_RUN} chmod 755 /usr/local/bin/useradd
            COPY shadow.sh /usr/local/bin/usermod
            {DOCKERFILE_RUN} chmod 755 /usr/local/bin/usermod
            COPY shadow.sh /usr/local/bin/userdel
            {DOCKERFILE_RUN} chmod 755 /usr/local/bin/userdel
            COPY shadow.sh /usr/local/bin/passwd
            {DOCKERFILE_RUN} chmod 755 /usr/local/bin/passwd
            COPY shadow.sh /usr/local/bin/groupadd
            {DOCKERFILE_RUN} chmod 755 /usr/local/bin/groupadd
            COPY shadow.sh /usr/local/bin/groupmod
            {DOCKERFILE_RUN} chmod 755 /usr/local/bin/groupmod
            COPY shadow.sh /usr/local/bin/groupdel
            {DOCKERFILE_RUN} chmod 755 /usr/local/bin/groupdel

            HEALTHCHECK --interval=60s --timeout=15s \
                        CMD smbclient -L \\localhost -U % -m SMB3
        """),
    )

    cli = ApplicationStackContainer(
        name="samba-client",
        pretty_name="Samba Client",
        custom_description=(
            "Samba is a feature-rich Open Source implementation of the SMB and "
            "Active Directory protocols for Linux and UNIX-like systems.\n\n"
            "This image comes with the Samba client and is {based_on_container}."
        ),
        from_target_image=f"{_build_tag_prefix(os_version)}/bci-micro:{OsContainer.version_to_container_os_version(os_version)}",
        os_version=os_version,
        is_latest=os_version in CAN_BE_LATEST_OS_VERSION,
        is_singleton_image=True,
        version="%%samba_version%%",
        version_in_uid=False,
        support_level=SupportLevel.L3,
        tag_version=format_version(
            samba_version := get_pkg_version("samba", os_version), ParseVersion.MINOR
        ),
        additional_versions=[format_version(samba_version, ParseVersion.MAJOR)],
        replacements_via_service=[
            Replacement(
                regex_in_build_description="%%samba_version%%", package_name="samba"
            )
        ],
        license="GPL-3.0-or-later",
        package_list=[
            "samba-client",
        ],
    )

    toolbox = ApplicationStackContainer(
        name="samba-toolbox",
        pretty_name="Samba Toolbox",
        custom_description=(
            "Samba is a feature-rich Open Source implementation of the SMB and "
            "Active Directory protocols for Linux and UNIX-like systems.\n\n"
            "This image comes with Samba tools, TDB tools and is {based_on_container}."
        ),
        from_target_image=f"{_build_tag_prefix(os_version)}/bci-micro:{OsContainer.version_to_container_os_version(os_version)}",
        os_version=os_version,
        is_latest=os_version in CAN_BE_LATEST_OS_VERSION,
        is_singleton_image=True,
        version="%%samba_version%%",
        version_in_uid=False,
        support_level=SupportLevel.L3,
        tag_version=format_version(
            samba_version := get_pkg_version("samba", os_version), ParseVersion.MINOR
        ),
        additional_versions=[format_version(samba_version, ParseVersion.MAJOR)],
        replacements_via_service=[
            Replacement(
                regex_in_build_description="%%samba_version%%", package_name="samba"
            )
        ],
        license="GPL-3.0-or-later",
        package_list=[
            "samba-client",
            "tdb-tools",
        ]
        # FIXME: unavailable on SLES
        + (["samba-test"] if os_version.is_tumbleweed else []),
    )

    SAMBA_SERVER_CONTAINERS.append(srv)
    SAMBA_CLIENT_CONTAINERS.append(cli)
    SAMBA_TOOLBOX_CONTAINERS.append(toolbox)
