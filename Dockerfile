FROM continuumio/miniconda3



RUN apt-get update \
    && apt-get install -y locales mercurial git python3-dev python3-pip libyaml-dev \
    && (curl https://sh.rustup.rs -sSf | sh -s -- -y) \
    && rm -rf /var/lib/apt/lists/* \
    && localedef -i en_US -c -f UTF-8 -A /usr/share/locale/locale.alias en_US.UTF-8 \
    && useradd -ms /bin/bash metasub

ENV LC_ALL C.UTF-8
ENV LANG C.UTF-8

ADD cap_env.yml /tmp/environment.yml

# USER metasub
WORKDIR /home/metasub
RUN conda env create -f=/tmp/environment.yml


ENTRYPOINT [ "/bin/bash", "-c" ]

RUN mkdir /home/metasub/manual_tools
WORKDIR /home/metasub/manual_tools
RUN /bin/bash -c "source activate cap \
    && source $HOME/.cargo/env \
    && cargo install finch"
WORKDIR /home/metasub/manual_tools
RUN /bin/bash -c "source activate cap \
    && git clone https://github.com/cdeanj/resistomeanalyzer.git \
    && cd resistomeanalyzer \
    && make \
    && mv resistome /bin"
WORKDIR /home/metasub/manual_tools
RUN /bin/bash -c "source activate cap \
    && git clone https://github.com/biobakery/metaphlan \
    && cd metaphlan2 \
    && mv metaphlan2.py /bin"
WORKDIR /home/metasub/manual_tools
RUN /bin/bash -c "source activate cap \
    && git clone https://github.com/snayfach/MicrobeCensus \
    && cd MicrobeCensus \
    && python setup.py install"

RUN /bin/bash -c "source activate cap \
    && pip install --ignore-installed PyYAML moduleultra==0.1.13"

RUN cd /home/metasub \
    && /bin/bash -c "source activate cap \
    && mkdir dbs \
    && mkdir base_repo \
    && mkdir repo \
    && cd /home/metasub/base_repo \
    && moduleultra init \
    && echo y | moduleultra install https://github.com/MetaSUB/MetaSUB_CAP \
    && moduleultra add pipeline metasub_cap"

ADD docker_pipeline_config.py /home/metasub/docker_pipeline_config.py
WORKDIR /home/metasub/repo
RUN /bin/bash -c "source activate cap"
