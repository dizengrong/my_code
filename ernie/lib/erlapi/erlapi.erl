-module(erlapi_app).

-behaviour(gen_server).

-compile(export_all).

-record(state, {
    src_path_list = []
    }).

start_link() ->
    gen_server:start_link({local, ?MODULE}, ?MODULE, [], []).

get_function_line(Module) ->
    gen_server:call(?MODULE, {request, get_function_line2, [Module]}).

init() ->
  {ok, #state{}}.



handle_call({request, Action, Args}, _From, State) ->
    {Reply, State1} = ?MODULE:Action(State, Args)
    {reply, Reply, State1}.



get_function_line2(State, [Module]) ->



