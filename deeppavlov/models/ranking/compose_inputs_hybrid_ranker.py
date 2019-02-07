# Copyright 2017 Neural Networks and Deep Learning lab, MIPT
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from logging import getLogger
from typing import Optional, Tuple, List

from deeppavlov.core.common.registry import register
from deeppavlov.core.models.estimator import Component

logger = getLogger(__name__)


@register("compose_inputs_hybrid_ranker")
class ComposeInputsHybridRanker(Component):

    def __init__(self,
                 context_depth: int = 1,
                 **kwargs):
         self.context_depth = context_depth
         self.num_turns_const = 10

    def __call__(self,
                 utterances_batch: list,
                 history_batch: list,
                 states_batch: Optional[list]=None):

        query_batch = []
        expanded_context_batch = []

        for i in range(len(utterances_batch)):
            full_context = history_batch[i][-self.num_turns_const + 1:] + [utterances_batch[i]]
            expanded_context = self._expand_context(full_context, padding="pre")

            query_batch.append(expanded_context[-1])   # search TF-IDF by last utterance only!
            # query_batch.append(" ".join(expanded_context))
            expanded_context_batch.append(expanded_context)

        # print("query:", query_batch)
        # print("expand_context:", expanded_context_batch)

        return query_batch, expanded_context_batch

    def _expand_context(self, context: List[str], padding: str) -> List[str]:
        """
        Align context length by using pre/post padding of empty sentences up to ``self.num_turns`` sentences
        or by reducing the number of context sentences to ``self.num_turns`` sentences.

        Args:
            context (List[str]): list of raw context sentences
            padding (str): "post" or "pre" context sentences padding

        Returns:
            List[str]: list of ``self.num_turns`` context sentences
        """
        if padding == "post":
            sent_list = context
            res = sent_list + (self.num_turns_const - len(sent_list)) * \
                  [''] if len(sent_list) < self.num_turns_const else sent_list[:self.num_turns_const]
            return res
        elif padding == "pre":
            # context[-(self.num_turns + 1):-1]  because the last item of `context` is always '' (empty string)
            sent_list = context[-self.num_turns_const:]
            if len(sent_list) <= self.num_turns_const:
                tmp = sent_list[:]
                sent_list = [''] * (self.num_turns_const - len(sent_list))
                sent_list.extend(tmp)

            for i in range(len(sent_list) - self.context_depth):
                sent_list[i] = ''  # erase context until the desired depth

            return sent_list