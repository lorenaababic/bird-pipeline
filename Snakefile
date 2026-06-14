# Bird Observation Pipeline - Snakemake Workflow

OUTPUT_DIR = "output"

rule all:
    input:
        f"{OUTPUT_DIR}/bird_report.csv"

rule scrape_species:
    output:
        temp("step1_done.txt")
    shell:
        """
        python3 scripts/step1_scrape_species.py --output {output}
        touch {output}
        """

rule consume_kafka:
    input:
        "step1_done.txt"
    output:
        temp("step2_done.txt")
    shell:
        """
        python3 scripts/step2_consume_kafka.py --output {output}
        touch {output}
        """

rule process_audio:
    input:
        "step2_done.txt"
    output:
        temp("step3_done.txt")
    params:
        audio_dir = "audio_files"
    shell:
        """
        python3 scripts/step3_process_audio.py --audio-dir {params.audio_dir} --output {output}
        touch {output}
        """

rule generate_report:
    input:
        "step3_done.txt"
    output:
        f"{OUTPUT_DIR}/bird_report.csv"
    params:
        species_filter = config.get("species_filter", ""),
        fuzzy_threshold = config.get("fuzzy_threshold", 80)
    shell:
        """
        python3 scripts/step4_generate_report.py \
            --output {output} \
            --species-filter "{params.species_filter}" \
            --fuzzy-threshold {params.fuzzy_threshold}
        """