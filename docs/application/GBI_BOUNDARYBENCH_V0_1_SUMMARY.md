# GBI BoundaryBench - preserved baseline and assessment update

The v0.1 result remains 0 accepted structured records in 768 executions of one
4B model over 256 held-out synthetic tasks and three evidence modes. It demonstrates
a failure at the model-output boundary, not useful zero-risk performance.

![Assessment update](figures/updated.svg)

The assessment update documents both GBI and DCSE reference execution, a canonical
dataset review, a separate real small-model experiment, and a deterministic
FHIR-format repair. The findings support a more useful distinction between
software execution, representation checks and eventual institutional validation.

Read [the results narrative](ASSESSMENT_RESULTS.md), [the revised landing page](../../README.md)
and [the limits on reproduction](../reproducibility_guide.md).
