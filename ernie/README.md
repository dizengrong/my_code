Ernie
=====

By Tom Preston-Werner (tom@mojombo.com)

Ernie is a BERT-RPC server implementation that uses an Erlang server to accept
incoming connections, and then delegates the request to custom modules that
you can write in any language (currently only Ruby and Erlang support is
included).

Modules that are written in Ruby or any non-Erlang language are known as
"external" modules and you must specify how many workers of each module should
be spawned. Requests against these modules are balanced between the workers.
Modules that are written in Erlang are known as "native" modules and run
within the Erlang server's runtime. Since these are spawned as lightweight
processes, there is no balancing necessary and much less communication
overhead when compared to external modules.

Ernie supports multiple heterogenous modules. For instance, you can have an
external Ruby module running 10 workers *and* a native Erlang module running
simultaneously. Ernie keeps track of sending requests to the proper module.
Using a technique called "shadowing," you can selectively optimize certain
external module functions with native code and Ernie will handle selecting the
correct function.

See the full BERT-RPC specification at [bert-rpc.org](http://bert-rpc.org).

Ernie currently supports the following BERT-RPC features:

* `call` requests
* `cast` requests

Ernie was developed for GitHub and is currently in production use serving
millions of RPC requests every day. The stability and performance have been
exemplary.

Ernie follows [Semantic Versioning](http://semver.org/) for release
versioning.

Installation
------------

Step 1: Install Erlang (R13B or higher).

    http://www.erlang.org/download.html

Step 2: Install Ernie:

    $ [sudo] gem install ernie


Running
-------

    Usage: ernie [command] [options]
        -c, --config CONFIG              Config file.
        -p, --port PORT                  Port.
        -l, --log-level                  Log level (0-4).
        -a, --access-log LOGFILE         Access log file.
        -d, --detached                   Run as a daemon.
        -P, --pidfile PIDFILE            Location to write pid file.
        --name NAME                      Erlang process name.
        --sname SNAME                    Erlang short process name.
        -E, --erlang ERLANG_OPTIONS      Options passed to Erlang VM.

    Commands:
      <none>                Start an Ernie server.
      reload-handlers       Gracefully reload all of the external handlers
                            and use the new code for all subsequent requests.
      stats                 Print a list of connection and handler statistics.

    Examples:
      ernie -d -p 9999 -c example.cfg
        Start the ernie server in the background on port 9999 using the
        example.cfg configuration file.

      ernie reload-handlers -p 9999
        Reload the handlers for the ernie server currently running on
        port 9999.

      ernie -c example.cfg -E '-run mymodule'
        Start the ernie server with an additional erlang module called
        'mymodule'


Configuration File
------------------

Ernie configuration files are written as a series of dotted Erlang terms. Each
term is a list of 2-tuples that specify options for a module.

### Native Modules

The form for native modules is:

    [{module, Module},
     {type, native},
     {codepaths, CodePaths}].

Where Module is an atom corresponding to the module name and CodePaths is a
list of strings representing the file paths that should be added to the
runtime's code path. These paths will be prepended to the code path and must
include the native module's directory and the directories of any dependencies.

### External Modules

The form for external modules is:

    [{module, Module},
     {type, external},
     {command, Command},
     {count, Count}].

Where Module is an atom corresponding to the module name, Command is a string
specifying the command to be executed in order to start a worker, and Count is
the number of workers to spawn.

### Shadowing

If you specify a native module and an external module of the same name (and in
that order), Ernie will inspect the native module to see if it has the
requested function exported and use that if it does. If it does not, then it
will fall back on the external module. This can be used to selectively
optimize certain functions in a module without any modifications to your
client code.

### Predicate Shadowing

In some circumstances it can be nice to conditionally shadow a function in an
external module based on the nature of the arguments. For example, you might
want requests for `math:fib(X)` to be routed to the external module when X is
less than 10, but to be handled by the native module when X is 10 or greater.
This can be accomplished by implementing a function `math:fib_pred(X)` in the
native module. Notice the `_pred` appended to the normal function name (pred
is short for predicate). If a function like this is present, Ernie will call
it with the requested arguments and if the return value is `true` the native
module will be used. If the return value is `false` the external module will
be used.


Example Configuration File
--------------------------

The following example config file informs Ernie of two modules. The first term
identifies a native module 'nat' that resides in the nat.beam file under the
'/path/to/app/ebin' directory. The second term specifies an external module
'ext' that will have 2 workers started with the command 'ruby
/path/to/app/ernie/ext.rb'.

    [{module, nat},
     {type, native},
     {codepaths, ["/path/to/app/ebin"]}].

    [{module, ext},
     {type, external},
     {command, "ruby /path/to/app/ernie/ext.rb"},
     {count, 2}].


Access Log
----------

If you have requested that an access log be written (using the -a or
--access-log option) then all requests will be logged to that file. Each
request is printed on a single line. The elements of the log line are as
follows (with comments on the right side):

    ACC                                  type of message [ ACC | ERR ]
    [2010-02-20T11:42:25.259750]         time the connection was accepted
    0.000053                             seconds from connection to processing start
    0.000237                             seconds from processing start to finish
    -                                    delimiter
    0                                    size of high queue at connect time
    0                                    size of low queue at connect time
    nat                                  type of handler [ nat | ext ]
    high                                 priority [ high | low ]
    -                                    delimiter
    {call,nat,add,[1,2]}                 message


Log lines are written when the request completes so they may appear out of
order with respect to connection time. To facilitate log rotation, Ernie will
create a new access log file if the current log file is moved or deleted.


Native (Erlang) Handler
-----------------------

Native handlers are written as normal Erlang modules. The exported functions
will become available to BERT-RPC clients.

### Example

    -module(nat).
    -export([add/2]).

    add(A, B) ->
      A + B.

### BERT-RPC Sequence Example

    -> {call, nat, add, [1, 2]}
    <- {reply, 3}


External (Ruby) Handler
-----------------------

Included in this gem is a library called `ernie` that makes it easy to write
Ernie handlers in Ruby. All you have to do is write a standard Ruby module and
expose it to Ernie and the functions of that module will become available to
BERT-RPC clients.

### Example

Using a Ruby module and Ernie.expose:

    require 'rubygems'
    require 'ernie'
    
    module Ext
      def add(a, b)
        a + b
      end
    end
    
    Ernie.expose(:ext, Ext)

### BERT-RPC Sequence Example

    -> {call, nat, add, [1, 2]}
    <- {reply, 3}

### Logging

You can have logging sent to a file by adding these lines to your handler:

    logfile('/var/log/ernie.log')
    loglevel(Logger::INFO)

This will log startup info, requests, and error messages to the log. Choosing
Logger::DEBUG will include the response (be careful, doing this can generate
very large log files).

### Autostart

Normally Ruby Ernie handlers will become active after the file has been loaded
in. you can disable this behavior by setting:

    Ernie.auto_start = false


Selecting Queue Priority
------------------------

Ernie maintains High and Low priority queues for incoming connections. If
there are any connections in the High priority queue, they will always be
processed first. If the High priority queue is empty, connections will be
processed from the Low priority queue. By default, connections go into the
High priority queue. To select a queue, an info BERP of the following form
must be sent preceding the call.

    -- {info, priority, Priority}

Where `Priority` is either the `high` or `low` atom. An example sequence where
the low priority queue is being selected would look like the following.

    -> {info, priority, low}
    -> {call, nat, add, [1, 2]}
    <- {reply, 3}


Using the BERTRPC gem to make calls to Ernie
--------------------------------------------

You can make BERT-RPC calls from Ruby with the [BERTRPC gem](http://github.com/mojombo/bertrpc):

    require 'bertrpc'

    svc = BERTRPC::Service.new('localhost', 8000)
    svc.call.ext.add(1, 2)
    # => 3


Contribute
----------

If you'd like to hack on Ernie, start by forking my repo on GitHub:

    http://github.com/mojombo/ernie

To get all of the dependencies, install the gem first. To run ernie from
source, you must first build the Erlang code:

    rake ebuild

The best way to get your changes merged back into core is as follows:

1. Clone down your fork
1. Create a topic branch to contain your change
1. Hack away
1. Add tests and make sure everything still passes by running `rake`
1. If you are adding new functionality, document it in the README.md
1. Do not change the version number, I will do that on my end
1. If necessary, rebase your commits into logical chunks, without errors
1. Push the branch up to GitHub
1. Send me (mojombo) a pull request for your branch


Copyright
---------

Copyright (c) 2009 Tom Preston-Werner. See LICENSE for details.
