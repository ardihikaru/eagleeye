# Copyright (c) 2017, 2020 ADLINK Technology Inc.
#
# This program and the accompanying materials are made available under the
# terms of the Eclipse Public License 2.0 which is available at
# http://www.eclipse.org/legal/epl-2.0, or the Apache License, Version 2.0
# which is available at https://www.apache.org/licenses/LICENSE-2.0.
#
# SPDX-License-Identifier: EPL-2.0 OR Apache-2.0
#
# Contributors:
#   ADLINK zenoh team, <zenoh@adlink-labs.tech>

import sys
import time
import argparse
import zenoh
from zenoh.net import config, SubInfo, Reliability, SubMode, Sample, resource_name
from zenoh.net.queryable import STORAGE

# --- Command line argument parsing --- --- --- --- --- ---
parser = argparse.ArgumentParser(
    prog='zn_storage',
    description='zenoh-net storage example')
parser.add_argument('--mode', '-m', dest='mode',
                    default='peer',
                    choices=['peer', 'client'],
                    type=str,
                    help='The zenoh session mode.')
parser.add_argument('--peer', '-e', dest='peer',
                    metavar='LOCATOR',
                    action='append',
                    type=str,
                    help='Peer locators used to initiate the zenoh session.')
parser.add_argument('--listener', '-l', dest='listener',
                    metavar='LOCATOR',
                    action='append',
                    type=str,
                    help='Locators to listen on.')
parser.add_argument('--selector', '-s', dest='selector',
                    default='/demo/example/**',
                    type=str,
                    help='The selection of resources to subscribe.')

args = parser.parse_args()
conf = { "mode": args.mode }
if args.peer is not None:
    conf["peer"] = ",".join(args.peer)
if args.listener is not None:
    conf["listener"] = ",".join(args.listener)
selector = args.selector

# zenoh-net code  --- --- --- --- --- --- --- --- --- --- ---

store = {}

def listener(sample):
    import logging

    ###

    L = logging.getLogger(__name__)

    ###

    import simplejson as json
    import time
    from datetime import datetime
    import ast
    import numpy as np

    # ####################### For tuple data
    # t0_decoding = time.time()
    # deserialized_bytes = np.frombuffer(sample.payload, dtype=[('id', 'U10'),
    #                                       ('store_enabled', '?'),
    #                                       ('timestamp', 'f'),
    #                                       ('image', [('pixel', 'i')], (1, 6220800))
    #                                       ])
    #
    # t1_decoding = (time.time() - t0_decoding) * 1000
    # L.warning(
    #     ('\n[%s] Latency deserialized_bytes (%.3f ms) \n' % (datetime.now().strftime("%H:%M:%S"), t1_decoding)))
    #
    # t0_decoding = time.time()
    # img_ori = deserialized_bytes["image"]["pixel"][0].reshape(1080, 1920, 3)
    # # print(">>> img_ori SHAPE:", img_ori.shape)
    #
    # t1_decoding = (time.time() - t0_decoding) * 1000
    # L.warning(
    #     ('\n[%s] Latency reformat image (%.3f ms) \n' % (datetime.now().strftime("%H:%M:%S"), t1_decoding)))
    # ######################## END for tuple data



    ############ For IMAGE ONLY
    t0_decoding = time.time()
    deserialized_bytes = np.frombuffer(sample.payload, dtype=np.int8)
    t1_decoding = (time.time() - t0_decoding) * 1000
    L.warning(
        ('\n[%s] Latency load ONLY numpy image (%.3f ms) \n' % (datetime.now().strftime("%H:%M:%S"), t1_decoding)))


    t0_decoding = time.time()
    deserialized_img = np.reshape(deserialized_bytes, newshape=(1080, 1920, 3))
    t1_decoding = (time.time() - t0_decoding) * 1000
    L.warning(
        ('\n[%s] Latency reformat image (%.3f ms) \n' % (datetime.now().strftime("%H:%M:%S"), t1_decoding)))
    ############ END For IMAGE ONLY

    # print(">>>> sample.data_info:", type(sample.data_info), sample.data_info)
    # print(">>>> sample.payload:", type(sample.payload.decode("utf-8")), sample.payload.decode("utf-8"))
    # print(">> [Storage listener] Received ('{}': '{}')"
    #       .format(sample.res_name, sample.payload.decode("utf-8")))

    # store consumed data
    store[sample.res_name] = (sample.payload, sample.data_info)


def query_handler(query):
    print(">> [Query handler   ] Handling '{}?{}'"
          .format(query.res_name, query.predicate))
    replies = []
    for stored_name, (data, data_info) in store.items():
        if resource_name.intersect(query.res_name, stored_name):
            query.reply(Sample(stored_name, data, data_info))


# initiate logging
zenoh.init_logger()

print("Openning session...")
session = zenoh.net.open(conf)

sub_info = SubInfo(Reliability.Reliable, SubMode.Push)

print("Declaring Subscriber on '{}'...".format(selector))
sub = session.declare_subscriber(selector, sub_info, listener)

print("Declaring Queryable on '{}'...".format(selector))
queryable = session.declare_queryable(
    selector, STORAGE, query_handler)

print("Press q to stop...")
c = '\0'
while c != 'q':
    c = sys.stdin.read(1)

sub.undeclare()
queryable.undeclare()
session.close()