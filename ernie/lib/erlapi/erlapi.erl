-module(erlapi).

% -behaviour(gen_server).

-compile(export_all).

-record(state, {
	root_path     = "",		%% 为project的根目录
	src_path_list = [],		%% 这里的path为相对于root_path的路径
	include_path  = []		%% 头文件搜索路径的列表
    }).

start_link() ->
    gen_server:start_link({local, ?MODULE}, ?MODULE, [], []).

%% Module is of string type
get_function_line(ReqModule, Line, CallModule, CallFunc) ->
    gen_server:call(?MODULE, {request, get_function_line2, [ReqModule, Line, CallModule, CallFunc]}).

set_project_root_path(Path) ->
	gen_server:cast(?MODULE, {request, set_project_root_path2, [Path]}). 

init([]) ->
  {ok, #state{}}.



handle_call({request, Action, Args}, _From, State) ->
    {Reply, State1} = ?MODULE:Action(State, Args),
    {reply, Reply, State1}.

handle_cast({request, Action, Args}, State) ->
    State1 = ?MODULE:Action(State, Args),
    {noreply, State1}.

set_project_root_path2(State, [Path]) ->
	Emakefile = Path ++ "/Emakefile",
	case filelib:is_file(Emakefile) of
		true ->
			{ok, Terms} = file:consult(Emakefile),
			Fun1 = fun({CodePath, _}, PathList) ->
				[atom_to_list(CodePath) | PathList]
			end,
			Fun2 = fun({_, OptionList}, IncludePathSet) ->
				case lists:keyfind(i, 1, OptionList) of
					false -> IncludePathSet;
					{i, P} ->
						sets:add_element(Path ++ "/" ++ P, IncludePathSet)
				end
			end,
			State1 = State#state{
						root_path     = Path,
						include_path  = sets:to_list(lists:foldl(Fun2, sets:new(), Terms)),
						src_path_list = lists:foldl(Fun1, [], Terms)};
		false ->
			State1 = State
	end,
	io:format("State is: ~p", [State1]),
	State1.

get_function_line2(State, [ReqModule, Line, CallModule, CallFunc]) ->
	ArgsNum = get_call_func_args_num(State, ReqModule, Line, CallModule, CallFunc),
	io:format("ArgsNum: ~w~n", [ArgsNum]),
	% {true, ReqFilename} = find_module_file(State#state.root_path, State#state.src_path_list, ReqModule),
	% Fun1 = fun(Tokens, Result) ->
	% 	case Tokens of
	% 		{function, _, _, _, ClauseList} ->

	% Reply = find_module_file(State#state.root_path, State#state.src_path_list, Module),
	% io:format("find_module_file return: ~w~n", [Reply]),
	Reply = false,
	% case Reply of
	% 	false -> Reply1 = false;
	% 	{true, Filename} ->
	% 		Forms = dynamic_compile:parse_file(Filename),

	{Reply, State}.
	
get_call_func_args_num(State, ReqModule, Line, CallModule, CallFunc) ->
	{true, ReqFilename} = find_module_file(State#state.root_path, State#state.src_path_list, ReqModule),
	Forms = dynamic_compile:parse_file(ReqFilename, State#state.include_path),
	parse_args_num(Forms, Line, CallModule, CallFunc).

parse_args_num([], _Line, _CallModule, _CallFunc) -> false;
parse_args_num([{function, _, _, _, ClauseList} | Rest], Line, CallModule, CallFunc) ->
	case parse_args_num2(ClauseList, Line, CallModule, CallFunc) of
		false ->
			parse_args_num(Rest, Line, CallModule, CallFunc);
		ArgsNum ->
			ArgsNum
	end;
parse_args_num([_ | Rest], Line, CallModule, CallFunc) ->
	parse_args_num(Rest, Line, CallModule, CallFunc).


parse_args_num2([], _Line, _CallModule, _CallFunc) -> false;
parse_args_num2([{clause, _, _, _, DataList} | Rest], Line, CallModule, CallFunc) ->
	case parse_args_num3(DataList, Line, CallModule, CallFunc) of
		false ->
			parse_args_num2(Rest, Line, CallModule, CallFunc);
		ArgsNum ->
			ArgsNum
	end;
parse_args_num2([_ | Rest], Line, CallModule, CallFunc) ->
	parse_args_num2(Rest, Line, CallModule, CallFunc).

parse_args_num3([], _Line, _CallModule, _CallFunc) -> false;
parse_args_num3([{call, Line, {remote, _, _Mod, _Fun}, Args} | _Rest], Line, _CallModule, _CallFunc) ->
	length(Args);
parse_args_num3([{call, Line, {atom, _, _Fun}, Args} | _Rest], Line, _CallModule, _CallFunc) ->
	length(Args);
parse_args_num3([_ | Rest], Line, CallModule, CallFunc) ->
	parse_args_num3(Rest, Line, CallModule, CallFunc).

find_module_file(_RootPath, [], _Module) -> false;
find_module_file(RootPath, [CodePath | Rest], Module) ->
	List = re:split(CodePath, "/", [{return, list}]),
	case find_module_file2(RootPath, List, Module) of
		false ->
			find_module_file(RootPath, Rest, Module);
		Finded ->
			Finded
	end.

%% 深度遍历
find_module_file2(_RootPath, [], _Module) -> false;
find_module_file2(RootPath, [Folder | Rest], Module) ->
	io:format("~nfind_module_file2, search path: ~s~n", [RootPath]),
	case Folder of
		"*" ->
			case has_module(RootPath, Module) of
				false ->
					find_module_file3(RootPath, Rest, Module);
				{true, FileFullName} ->
					{true, FileFullName}
			end;
		_ ->
			find_module_file2(RootPath ++ "/" ++ Folder, Rest, Module)
	end.

find_module_file3(RootPath, Folders, Module) ->
	{ok, Filenames} = file:list_dir(RootPath),
	Filenames1 = [RootPath ++ "/" ++ Name || Name <- Filenames],
	FoldersFullname = lists:filter(fun filelib:is_dir/1, Filenames1),
	
	io:format("~nFoldersFullname1: ~p~n", [FoldersFullname]),
	find_module_file4(FoldersFullname, Folders, Module).

find_module_file4([], _Folders, _Module) -> false;
find_module_file4([FolderFullname | Rest], Folders, Module) ->
	case find_module_file2(FolderFullname, Folders, Module) of
		false ->
			find_module_file4(Rest, Folders, Module);
		Finded ->
			Finded
	end.

has_module(Folder, Module) ->
	{ok, Filenames} = file:list_dir(Folder),
	case lists:member(Module ++ ".erl", Filenames) of
		true ->
			{true, Folder ++ "/" ++ Module ++ ".erl"};
		_ -> 
			false
	end.