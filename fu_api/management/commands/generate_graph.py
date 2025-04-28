import os
import itertools
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.colors as mc
from scipy.stats import gaussian_kde
from django.core.management.base import BaseCommand, CommandError


class Command(BaseCommand):

    def add_arguments(self, parser):
        parser.add_argument('csv_path', type=str, help='Path to the CSV file.')

    def handle(self, *args, **options):
        csv_path = options['csv_path']
        if not os.path.exists(csv_path):
            raise CommandError(f"CSV file does not exist: {csv_path}")

        df = pd.read_csv(csv_path)

        if 'label' not in df.columns:
            raise CommandError("CSV file must contain a 'label' column.")

        df_positive = df[df['label'] == 1.0]
        df_negative = df[df['label'] == 0.0]

        if len(df_negative) > len(df_positive):
            df_negative = df_negative.sample(n=len(df_positive), random_state=42)
        elif len(df_positive) > len(df_negative) and len(df_negative) > 0:
            df_positive = df_positive.sample(n=len(df_negative), random_state=42)

        balanced_df = pd.concat([df_negative, df_positive])

        feature_columns = [col for col in balanced_df.columns if col != 'label']

        output_dir = os.path.join(os.getcwd(), "graphs")
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)

        base_colors = {0.0: 'red', 1.0: 'blue'}

        for x_feature, y_feature in itertools.combinations(feature_columns, 2):
            plt.figure(figsize=(10, 6))
            for label, group in balanced_df.groupby('label'):
                x = group[x_feature].values
                y = group[y_feature].values

                xy = np.vstack([x, y])
                density = gaussian_kde(xy)(xy)

                norm_density = (density - density.min()) / (density.max() - density.min() + 1e-6)
                darken_factor = norm_density * 0.5

                colors_adjusted = [self.adjust_color(base_colors[label], factor) for factor in darken_factor]

                plt.scatter(
                    x, y,
                    label=f"Label {int(label)}",
                    color=colors_adjusted,
                    linewidth=0.5,
                )

            plt.xlabel(x_feature)
            plt.ylabel(y_feature)
            plt.title(f"Scatter Plot: {x_feature} vs {y_feature}")
            plt.legend()
            plt.tight_layout()

            output_path = os.path.join(output_dir, f"graph_{x_feature}_vs_{y_feature}.png")
            plt.savefig(output_path)
            plt.close()
            self.stdout.write(self.style.SUCCESS(f"Graph saved as {output_path}"))

        self.stdout.write(self.style.SUCCESS("All graphs generated successfully."))

    def adjust_color(color, factor):
        base = np.array(mc.to_rgb(color))
        new_color = base * (1 - factor)
        return new_color 
