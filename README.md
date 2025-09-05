# Bradley Terry Model For Sports Team Rankings

An implementation of a Bradley Terry Model to generate [KRACH Rankings](https://hockeypowerrankings.com/About.html) for an ice hockey league that I worked with.

**Bradley–Terry model**

The **Bradley–Terry model** is a [probability model](https://en.wikipedia.org/wiki/Probability_theory) for the outcome of pairwise comparisons between items, teams, or objects.
Given a pair of items $i$ and $j$ drawn from some [population](https://en.wikipedia.org/wiki/Population_(statistics)), it estimates the probability that the [pairwise comparison](https://en.wikipedia.org/wiki/Pairwise_comparison_(psychology)) $i > j$ turns out true, as

$$
\Pr(i > j) = \frac{p_i}{p_i + p_j}
$$
*Equation 1*

where $p_i$ is a positive [real-valued](https://en.wikipedia.org/wiki/Real_number) score assigned to individual $i$.  The comparison $i > j$ can be read as "$i$ is preferred to $j$", "$i$ ranks higher than $j$", or "$i$ beats $j$", depending on the application.

For example, $p_i$ might represent the skill of a team in a sports tournament and $\Pr(i > j)$ the probability that $i$ wins a game against $j$.  Or $p_i$ might represent the quality or desirability of a commercial product and $\Pr(i > j)$ the probability that a consumer will prefer product $i$ over product $j$.


### Reference

[Bradley-Terry Model | Wikipedia](https://en.wikipedia.org/wiki/Bradley%E2%80%93Terry_model)