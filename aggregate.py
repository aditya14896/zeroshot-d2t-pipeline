#!/usr/bin/env python3

import argparse
import logging
import numpy as np
import os
import re
import torch
import json
import pytorch_lightning as pl

from pprint import pprint as pp
from utils.tokenizer import Tokenizer
from model import AggTrainingModule
from dataloader import AggDataModule
from inference import AggInferenceModule

class AggModule:
    def __init__(self, model_path, separator):
        self.model = AggInferenceModule(args, model_path=model_path)
        self.separator = separator

    def aggregate_dataset(self, in_filename, out_filename):
        output = {
            "data" : []
        }
        with open(in_filename) as in_file:
            j = json.load(in_file)

            for i, example in enumerate(j["data"]):
                sents = example["text"]

                out = []

                if len(sents) == 1:
                    out = sents
                else:
                    seps = self.model.predict(sents)
                    for j in range(len(sents)):
                        out.append(sents[j])

                        if j < len(seps) and seps[j] == 1:
                            out.append(self.separator)
                print(i)
                print(out)
                print("================")
                example_sorted = {
                    "text" : " ".join(out),
                    "labels" : example["labels"]
                }
                output["data"].append(example_sorted)

        with open(os.path.join(out_filename), "w") as f:
            json.dump(output, f, indent=4, ensure_ascii=False)

    def aggregate_dataset_eval(self, in_filename):
        correct_agg = 0
        correct_random = 0
        correct_agg_perpos = 0
        correct_random_perpos = 0
        total = 0
        total_pos = 0

        with open(in_filename) as in_file:
            j = json.load(in_file)
            for i, example in enumerate(j["data"]):
                total += 1
                sents = example["text"]

                if len(sents) == 1:
                    # skip trivial examples
                    continue

                out = []
                seps = self.model.predict(sents)

                if seps in example['labels']:
                    correct_agg += 1

                random_seps = list(np.random.randint(2, size=len(seps)))

                if random_seps in example['labels']:
                    correct_random += 1

                for j, (s, r) in enumerate(zip(seps, random_seps)):
                    total_pos += 1
                    gold_pos = [e[j] for e in example['labels']]

                    if s in gold_pos:
                        correct_agg_perpos += 1
                    if r in gold_pos:
                        correct_random_perpos += 1


        print(f"Accuracy - random: {correct_random/total:.2f} ({correct_random}/{total})")
        print(f"Accuracy - agg module: {correct_agg/total:.2f} ({correct_agg}/{total})")

        print(f"Accuracy - random per position: {correct_random_perpos/total_pos:.2f} ({correct_random_perpos}/{total_pos})")
        print(f"Accuracy - agg module per position: {correct_agg_perpos/total_pos:.2f} ({correct_agg_perpos}/{total_pos})")

logging.basicConfig(format='%(asctime)s - %(levelname)s - %(message)s', level=logging.INFO, datefmt='%H:%M:%S')
logger = logging.getLogger(__name__)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--exp_dir", default="experiments", type=str,
        help="Base directory of the experiment.")
    parser.add_argument("--in_dir", type=str, required=True,
        help="Directory with the dataset to sort.")
    parser.add_argument("--out_dir", type=str, default=None,
        help="Output directory (default name uses a suffix \"_agg\")")
    parser.add_argument("--experiment", type=str, required=True,
        help="Experiment name.")
    parser.add_argument("--seed", default=42, type=int,
        help="Random seed.")
    parser.add_argument("--max_threads", default=4, type=int,
        help="Maximum number of threads.")
    parser.add_argument("--beam_size", default=1, type=int,
        help="Beam size.")
    parser.add_argument("--gpus", default=1, type=int,
        help="Number of GPUs.")
    parser.add_argument("--max_length", type=int, default=1024,
        help="Maximum number of tokens per example")
    parser.add_argument("--checkpoint", type=str, default="model.ckpt",
        help="Override the default checkpoint name 'model.ckpt'.")
    parser.add_argument('--splits', type=str, nargs='+', default=["test"],
                    help='Dataset splits (e.g. train dev test)')
    parser.add_argument('--eval', action="store_true",
                    help='Run evaluation')
    parser.add_argument("--separator", type=str, default="<sep>",
        help="Separator token.")
    args = parser.parse_args()

    logger.info(args)

    torch.manual_seed(args.seed)
    np.random.seed(args.seed)
    torch.set_num_threads(args.max_threads)

    model_path = os.path.join(args.exp_dir, args.experiment, args.checkpoint)
    dam = AggModule(model_path,
        args.separator)

    if args.out_dir is None:
        out_dir = args.in_dir + "_agg"
    else:
        out_dir = args.out_dir

    os.makedirs(out_dir, exist_ok=True)

    for split in args.splits:
        if args.eval:
            dam.aggregate_dataset_eval(
                in_filename=os.path.join(args.in_dir, f"{split}.json"),
                # out_filename=os.path.join(out_dir, f"{split}.out"),
            )
        else:
            dam.aggregate_dataset(
                in_filename=os.path.join(args.in_dir, f"{split}.json"),
                out_filename=os.path.join(out_dir, f"{split}.json")
            )