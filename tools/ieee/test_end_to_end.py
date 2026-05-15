#!/usr/bin/env python3
"""
End-to-end test for IEEE formatting toolkit.
Creates a sample IEEE paper, validates it, and tests BibTeX parsing.
"""

import os
import tempfile

from tools.ieee.formatter import build_ieee_paper
from tools.ieee.validator import validate, print_report
from tools.ieee.reference_formatter import parse_plain_text_refs


def test_formatter_and_validator():
    """Build a sample paper and validate it."""
    output = r"tools\ieee\templates\test_output.docx"

    sections = [
        {
            "title": "INTRODUCTION",
            "paragraphs": [
                "This paper addresses the critical challenge of data preprocessing "
                "for anomaly detection in industrial energy consumption systems.",
                "Our approach integrates physics-informed rules with advanced feature engineering.",
            ],
            "subsections": [
                {
                    "title": "Motivation",
                    "paragraphs": [
                        "Industrial steel production consumes 7-9% of global energy.",
                    ],
                },
            ],
        },
        {
            "title": "PROPOSED FRAMEWORK",
            "paragraphs": [
                "We propose a multi-stage pipeline transforming raw sensor data into "
                "a 64-dimensional feature space.",
            ],
        },
    ]

    refs = parse_plain_text_refs([
        "Steel Industry Energy Consumption - UCI ML Repository, 2018.",
        "IEEE Standard for Modeling and Simulation, IEEE Std 1730-2010.",
    ])

    build_ieee_paper(
        output_path=output,
        title="Test IEEE Paper: Data Preprocessing for Anomaly Detection",
        authors="Test Author\nDepartment of Data Science\nTest University",
        abstract="This is a test abstract for validation purposes. " * 5,
        keywords="Data preprocessing, anomaly detection, time series, feature engineering",
        sections=sections,
        references=refs,
    )

    report = validate(output)
    print_report(report)

    if report["total_issues"] == 0:
        print("\nALL TESTS PASSED")
    else:
        print(f"\n{report['total_issues']} issue(s) found -- review above.")

    # Cleanup test file
    if os.path.exists(output):
        os.remove(output)
        print(f"Cleaned up: {output}")


if __name__ == "__main__":
    test_formatter_and_validator()
