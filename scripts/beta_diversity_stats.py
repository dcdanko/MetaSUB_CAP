import sys
import click
from scipy import pdist, squareform, entropy
from numpy.linalg import norm
from math import sqrt
from json import dumps as jdumps
import pandas as pd


class LevelNotFoundException(Exception):
    pass


def checkLevel(taxon, level):
    if level == 'species':
        return ('s__' in taxon) and ('t__' not in taxon)
    elif level == 'genus':
        return ('g__' in taxon) and ('s__' not in taxon)
    raise LevelNotFoundException()


def jensenShannonDistance(P, Q):
    _P = P / norm(P, ord=1)
    _Q = Q / norm(Q, ord=1)
    _M = 0.5 * (_P + _Q)
    J = 0.5 * (entropy(_P, _M) + entropy(_Q, _M))
    return sqrt(J)


class SampleSet:

    def __init__(self, tool, mpas):
        self.tool = tool
        self.mpaFiles = []
        for i in range(0, len(mpas) + 1, 2):
            self.mpaFiles.append((mpas[i], mpas[i + 1]))

    def parse(self, level):
        mpas = {name: Sample.parseMPA(name, mpaf, level).abunds
                for name, mpaf in self.mpaFiles}
        self.mpas = pd.DataFrame(mpas)

    def distanceMatrix(self, metric):
        X = self.mpas.as_matrix()
        if metric == 'jensen_shannon_distance':
            distm = squareform(pdist(X, jensenShannonDistance))
        distm = pd.DataFrame(distm, index=self.mpas.index)
        return distm.to_dict()


class Sample:

    def __init__(self, sname, level):
        self.sname = sname
        self.level = level
        self.abunds = {}

    def addLine(self, line):
        taxon, abund = line.split()
        if checkLevel(taxon, self.level):
            self.abunds[taxon] = float(abund)

    @classmethod
    def parseMPA(ctype, name, mpaFile, level):
        sample = Sample(name, level)
        with open(mpaFile) as mF:
            for line in mF:
                sample.addLine(line)
        return sample


@click.command()
@click.option('-t', '--tool-set', nargs=-1, multiple=True)
def main(toolSets):
    sampleSets = []
    for toolSet in toolSets:
        tool = toolSet[0]
        mpas = toolSet[1:]
        sampleSets.append(SampleSet(tool, mpas))

    obj = {
        'species': {
            'jensen_shannon_distance': {},
        },
        'genus': {
            'jensen_shannon_distance': {},
        }
    }
    for level in obj.keys():
        for sampleSet in sampleSets:
            sampleSet.parse(level)
            tool = sampleSet.tool
            for metric in obj[level].keys():
                obj[level][metric][tool] = sampleSet.distanceMatrix(metric)
    sys.stdout.write(jdumps(obj))


if __name__ == '__main__':
    main()