import click


@click.command()
@click.option("--gold-file")
@click.option("--pred-file")
def main(gold_file: str, pred_file: str):
    g = open(gold_file)
    p = open(pred_file)
    for gold, pred in zip(g, p):
        golds = gold.rstrip("\n").rstrip(" ").split(" ")
        preds = pred.rstrip("\n").rstrip(" ").split(" ")
        assert len(golds) == len(preds)
        for gi, pi in zip(golds, preds):
            surface, gold_netag = gi.split("/")
            _, pred_netag = pi.split("/")
            print(f"{surface} _ {gold_netag} {pred_netag}")
        print()
    g.close()
    p.close()


if __name__ == "__main__":
    main()
