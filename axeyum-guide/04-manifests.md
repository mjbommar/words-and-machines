# Evidence manifests

Every active machine claim owns one manifest under the claims artifact tree.
The manifest binds:

- claim statement, scope, and exclusions;
- semantic package names, versions, paths, and digests;
- evidence paths, roles, and raw digests;
- producer command and version;
- checker command, version, and expected result;
- negative-control command, mutation, and expected failure;
- Axeyum revision and reproduction environment;
- trust class; and
- limitations.

The active trust classes are trace, computation, verdict, certificate, and
kernel. Definitions live in semantic packages and do not acquire a stronger
class merely because a package parses.

The structural artifact checker validates fields, repository-local paths, and
digests. Object checking binds manifests to book claims. Runtime checking
executes positive and negative routes.

No active manifest may point into the research archive.
