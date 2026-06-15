import argparse
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from pathlib import Path

def generate_visualization(input_path, output_path):
 
    print(f"Reading report: {input_path}")
    df = pd.read_csv(input_path)

    if df.empty:
        print(" Nema podataka za vizualizaciju")
        fig, ax = plt.subplots(figsize=(8, 4))
        ax.text(0.5, 0.5, "No data available", ha='center', va='center', fontsize=14)
        ax.axis('off')
        Path(output_path).parent.mkdir(parents=True, exist_ok=True)
        plt.savefig(output_path, dpi=150, bbox_inches='tight')
        print(f"✓ Placeholder graf spremljen: {output_path}")
        return

    df_sorted = df.sort_values("total_observations", ascending=True)

    fig, axes = plt.subplots(1, 2, figsize=(14, max(5, len(df_sorted) * 0.6 + 2)))
    fig.suptitle("Bird Observation Pipeline – Report", fontsize=14, fontweight='bold')

    ax1 = axes[0]
    y_pos = np.arange(len(df_sorted))
    ax1.barh(y_pos, df_sorted["classified_observations"],
             color="#4A90D9", label="Audio classifications")
    ax1.barh(y_pos, df_sorted["kafka_observations"],
             left=df_sorted["classified_observations"],
             color="#E8A838", label="Kafka observations")

    ax1.set_yticks(y_pos)
    ax1.set_yticklabels(df_sorted["common_name"], fontsize=9)
    ax1.set_xlabel("Broj opažanja")
    ax1.set_title("Opažanja po vrsti ptica")
    ax1.legend(loc="lower right", fontsize=8)
    ax1.grid(axis='x', linestyle='--', alpha=0.5)

    for i, (classified, kafka) in enumerate(zip(df_sorted["classified_observations"],
                                                  df_sorted["kafka_observations"])):
        total = classified + kafka
        ax1.text(total + 0.05, i, str(total), va='center', fontsize=8)

    ax2 = axes[1]
    if "family" in df.columns and df["family"].notna().any():
        family_counts = df.groupby("family")["total_observations"].sum()
        family_counts = family_counts[family_counts > 0]
        if not family_counts.empty:
            ax2.pie(family_counts, labels=family_counts.index,
                    autopct='%1.0f%%', startangle=140,
                    textprops={'fontsize': 8})
            ax2.set_title("Raspodjela opažanja po familijama")
        else:
            ax2.axis('off')
    else:
        ax2.axis('off')

    plt.tight_layout()
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    plt.savefig(output_path, dpi=150, bbox_inches='tight')
    print(f" Graf spremljen: {output_path}")

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", default="output/bird_report.csv")
    parser.add_argument("--output", default="output/bird_report.png")
    args = parser.parse_args()

    print("Starting Step 5 - Visualize Report...")
    try:
        generate_visualization(args.input, args.output)
        print(" Step 5 completed")
    except Exception as e:
        print(f"ERROR in Step 5: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()