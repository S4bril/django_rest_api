import itertools
import os

import matplotlib.pyplot as plt
import pandas as pd
from django.core.management.base import BaseCommand, CommandError


class Command(BaseCommand):

    def add_arguments(self, parser):
        parser.add_argument("csv_path", type=str, help="Path to the CSV file.")

    def handle(self, *args, **options):
        csv_path = options["csv_path"]
        if not os.path.exists(csv_path):
            raise CommandError(f"CSV file does not exist: {csv_path}")

        df = pd.read_csv(csv_path)

        df_positive = df[df["label"] == 1.0]
        df_negative = df[df["label"] == 0.0]

        df_negative = df_negative.sample(n=len(df_positive), random_state=42)

        balanced_df = pd.concat([df_negative, df_positive])

        feature_columns = [col for col in balanced_df.columns if col != "label"]

        output_dir = os.path.join(os.getcwd(), "graphs")
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)

        base_colors = {0.0: "#b92e2e", 1.0: "#4a9438"}

        for x_feature, y_feature in itertools.combinations(feature_columns, 2):
            plt.figure(figsize=(10, 6))
            for label, group in balanced_df.groupby("label"):
                x = group[x_feature].values
                y = group[y_feature].values

                plt.scatter(
                    x, y, label=f"Label {int(label)}", color=base_colors[label], s=15
                )

            plt.xlabel(x_feature)
            plt.ylabel(y_feature)
            plt.title(f"Scatter Plot: {x_feature} vs {y_feature}")
            plt.legend()
            plt.tight_layout()

            output_path = os.path.join(
                output_dir, f"graph_{x_feature}_vs_{y_feature}.png"
            )
            plt.savefig(output_path)
            plt.close()
            self.stdout.write(self.style.SUCCESS(f"Graph saved as {output_path}"))

        self.stdout.write(self.style.SUCCESS("All graphs generated successfully."))
