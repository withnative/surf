# Build and test

Surf requires Rust 1.85 or later.

```sh
cargo build --locked
cargo test --locked
cargo run --locked
```

The server listens on port `8080` by default. Set `PORT` to use another port. A generic
container build is also available:

```sh
docker build -t surf .
docker run --rm -p 8080:8080 surf
```

Ordinary local and archive builds deliberately report source metadata as unavailable;
they never combine the current checkout's commit with Surf's public repository URL. A
production build must explicitly provide a matching full public commit and URL:

```sh
SURF_GIT_SHA=$(git rev-parse HEAD)
docker build \
  --build-arg SURF_GIT_SHA="$SURF_GIT_SHA" \
  --build-arg SURF_SOURCE_URL="https://github.com/withnative/surf/commit/$SURF_GIT_SHA" \
  -t surf .
```

The build stops if either value is missing, the SHA is not full lowercase hexadecimal,
or the URL does not identify that exact commit in `withnative/surf`. Deployment must
still verify that the commit is public and is the source actually being built.

The hosted service follows the repository's documented
[merge-to-`main` production and rollback flow](production-deployment.md). Railway's
GitHub build supplies the exact triggering SHA and derives the matching URL during the
same container build; operators do not maintain those two values separately.

The official hosted endpoint is the supported product. The source is intentionally
inspectable, runnable, and forkable, but Native does not promise operational support or
automatic framework updates for self-hosted deployments. Fork operators own their
deployment and update policy.
