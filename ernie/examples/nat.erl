-module(nat).
-export([add/2, fib/1, die/1, parse/0]).

add(A, B) ->
  A + B.

fib(0) -> 1;
fib(1) -> 1;
fib(N) when N > 1 -> fib(N - 1) + fib(N - 2).

die(X) ->
  X = 10.

parse() ->
	% {ok, S} = file:read_file("../examples/nat.erl"),
	% S1 = binary_to_list(S),

	{ok, F} = file:open("../examples/"++atom_to_list(?MODULE)++".erl", [read]),
    {ok, S} = file:read(F, 9999999),

	% {ok, Tokens, _} = erl_scan:string(S),
	% Tokens = [{'-',2},{atom,2,export},{'(',2},{'[',2},{atom,2,foo},{'/',2},{integer,2,0},{']',2},{')',2},{dot,2}],
	Tokens = [{'-',1},
        {atom,1,module},
        {'(',1},
        {atom,1,nat},
        {')',1},
        {dot,1},
        {'-',2},
        {atom,2,export},
        {'(',2},
        {'[',2},
        {atom,2,add},
        {'/',2},
        {integer,2,2},
        {',',2},
        {atom,2,fib},
        {'/',2},
        {integer,2,1},
        {',',2},
        {atom,2,die},
        {'/',2},
        {integer,2,1},
        {',',2},
        {atom,2,parse},
        {'/',2},
        {integer,2,0},
        {']',2},
        {')',2},
        {dot,2}],
	io:format("Tokens:~p~n", [Tokens]),
	{ok, AbsForm} = erl_parse:parse_form(Tokens),
	io:format("~p~n", [AbsForm]).