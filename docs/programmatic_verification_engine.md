# Programmatic verification - review scope

The baseline research separates proposed structured results from deterministic
benchmark scoring. v0.1 includes generator-reference comparisons and checks for
identity, terminology/version, time and required evidence. Those references are
not clinical authority.

![Assessment update](application/figures/updated.svg)

Later GBI and DCSE reference-suite outcomes are summarized here without shipping
the implementation. The report-consistency checker in `src/` is a new, smaller
publication utility. It validates the included outcome tables and file inventory;
it is not the programmatic verification engine being studied.

The recorded FHIR-format result is also a separate deterministic adapter study.
Its schema checks must not be silently promoted into full FHIR or clinical
validation. Running the report-consistency checker does not reconstruct omitted source.
