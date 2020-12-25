import sys

import click


@click.command("main")
@click.option("--output", "-o", default="/dev/stdout")
@click.option("--output-layer", "-O", default=2, type=int)
def main(output: str, output_layer: int):
    fp = open(output, "w")
    for line in sys.stdin:
        line = line.rstrip("\n")
        if line.startswith("* "):
            if output_layer == 2:
                _, chunkd_id, _, _ = line.split(" ")
                # NOTE: To use CaboCha, we replace all dependency types with D (normal)
                line = f"* {chunkd_id} -1D"
            elif output_layer == 1:
                continue
            else:
                raise Exception("Unsupported output layer")
        print(line, file=fp)
    fp.close()


if __name__ == "__main__":
    main()
