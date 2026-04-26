# stratabench

Reproducible, content-addressed LLM evaluations with auditable provenance.

Every benchmark score this harness produces is paired with a provenance hash
covering the eval dataset version, prompt template, decoding configuration,
model identifier, and harness code. Same inputs + same harness = same hash.
Match the hash and you've reproduced the methodology — even if the numbers
themselves drift because of provider non-determinism.

## Status

**Under construction.** Pre-v1.

The plan is in [`docs/methodology.md`](docs/methodology.md). What's shipping
in v1:

- A runnable [Strata](https://forge-labs-dev.github.io/strata/) notebook that
  scores any model in the registry across a fixed eval bundle.
- ~10 frontier and open models scored end-to-end with provenance hashes
  published alongside.
- A methodology writeup explaining what's deterministic, what isn't, and
  how to verify a third-party reproduction.

## License

MIT. See [LICENSE](LICENSE).
