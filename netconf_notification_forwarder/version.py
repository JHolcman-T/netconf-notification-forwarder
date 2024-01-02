# release
major = "0"
minor = "0"
patch = "0"

# pre-release
pre_type = "preview"
pre_N = "0"
pre = pre_type + pre_N

# dev-release
dev_type = "dev"
dev_N = "0"
dev = dev_type + dev_N

__version__ = ".".join(
    filter(
        None,
        (
            major,
            minor,
            patch + pre,
            dev,
        ),
    ),
)
