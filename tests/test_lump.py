import os
thisdir = os.path.dirname(__file__)
thisdir = os.path.abspath(thisdir)

import khmer
import screed

## Below, 'fakelump.fa' is an artificial data set of 3x1 kb sequences in
## which the last 79 bases are common between the 3 sequences.

def test_fakelump_together():
    fakelump_fa = os.path.join(thisdir, 'test-data/fakelump.fa')

    ht = khmer.new_hashbits(32, 1e7, 4)
    ht.consume_fasta_and_tag(fakelump_fa)

    subset = ht.do_subset_partition(0, 0)
    ht.merge_subset(subset)
    
    (n_partitions, n_singletons) = ht.count_partitions()
    assert n_partitions == 1, n_partitions

# try loading stop tags from previously saved
def test_fakelump_stop():
    fakelump_fa = os.path.join(thisdir, 'test-data/fakelump.fa')
    fakelump_fa_stop = os.path.join(thisdir, 'test-data/fakelump.fa.stoptags')

    ht = khmer.new_hashbits(32, 1e7, 4)
    ht.consume_fasta_and_tag(fakelump_fa)

    ht.load_stop_tags(fakelump_fa_stop)

    subset = ht.do_subset_partition(0, 0, True)
    ht.merge_subset(subset)
    
    (n_partitions, n_singletons) = ht.count_partitions()
    assert n_partitions == 3, n_partitions

# check specific insertion of stop tag
def test_fakelump_stop2():
    fakelump_fa = os.path.join(thisdir, 'test-data/fakelump.fa')

    ht = khmer.new_hashbits(32, 1e7, 4)
    ht.consume_fasta_and_tag(fakelump_fa)

    ht.add_stop_tag('GGGGAGGGGTGCAGTTGTGACTTGCTCGAGAG')

    subset = ht.do_subset_partition(0, 0, True)
    ht.merge_subset(subset)
    
    (n_partitions, n_singletons) = ht.count_partitions()
    assert n_partitions == 3, n_partitions

# try repartitioning
def test_fakelump_repartitioning():
    fakelump_fa = os.path.join(thisdir, 'test-data/fakelump.fa')
    fakelump_fa_foo = os.path.join(thisdir, 'test-data/fakelump.fa.stopfoo')

    ht = khmer.new_hashbits(32, 1e7, 4)
    ht.consume_fasta_and_tag(fakelump_fa)

    subset = ht.do_subset_partition(0, 0)
    ht.merge_subset(subset)
    
    (n_partitions, n_singletons) = ht.count_partitions()
    assert n_partitions == 1, n_partitions

    # now, break partitions on any k-mer that you see more than once
    # on big excursions, where big excursions are excursions 40 out
    # that encounter more than 82 k-mers.  This should specifically
    # identify our connected sequences in fakelump...

    EXCURSION_DISTANCE=40
    EXCURSION_KMER_THRESHOLD=82
    EXCURSION_KMER_COUNT_THRESHOLD=1
    counting = khmer.new_counting_hash(32, 1e7, 4)

    ht.repartition_largest_partition(None, counting,
                                     EXCURSION_DISTANCE,
                                     EXCURSION_KMER_THRESHOLD,
                                     EXCURSION_KMER_COUNT_THRESHOLD)

    ht.save_stop_tags(fakelump_fa_foo)

    # ok, now re-do everything with these stop tags, specifically.

    ht = khmer.new_hashbits(32, 1e7, 4)
    ht.consume_fasta_and_tag(fakelump_fa)
    ht.load_stop_tags(fakelump_fa_foo)

    subset = ht.do_subset_partition(0, 0, True)
    ht.merge_subset(subset)
    
    (n_partitions, n_singletons) = ht.count_partitions()
    assert n_partitions == 3, n_partitions
