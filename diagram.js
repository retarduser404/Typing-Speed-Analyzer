flowchart TB
    %% Modules
    subgraph "CLI Application"
        direction TB
        UI_Module["User Interface Module"]:::ui
        Input_Handler["Input Handler"]:::logic
        Game_Controller["Game Controller / Typing Engine"]:::logic
        Stats_Calc["Statistics Calculator"]:::logic
        subgraph "Data Persistence" 
            direction TB
            Para_Loader["Paragraph Loader"]:::persistence
            Score_Storage["Score Storage"]:::persistence
        end
        Config["Configuration"]:::config
    end

    %% External Files
    paras_txt["paras.txt"]:::data
    scores_json["scores.json"]:::data
    README["README.md"]:::doc
    LICENSE["LICENSE"]:::doc

    %% Startup flow
    paras_txt -->|"load paragraphs"| Para_Loader
    scores_json -->|"load past scores"| Score_Storage
    Para_Loader -->|"provide paragraphs"| Game_Controller
    Score_Storage -->|"provide leaderboard data"| Game_Controller

    %% Runtime flow
    User["User"]:::external -->|keystrokes| Input_Handler
    Input_Handler -->|parsed input| Game_Controller
    Game_Controller -->|render menus/text| UI_Module
    Game_Controller -->|on completion: test data| Stats_Calc
    Stats_Calc -->|stats results| UI_Module
    Stats_Calc -->|update leaderboard entry| Score_Storage
    Score_Storage -->|write to JSON| scores_json

    %% Configuration
    Config -->UI_Module
    Config -->Game_Controller
    Config -->Stats_Calc

    %% Documentation links
    README -->|documentation| UI_Module
    LICENSE -->|license| UI_Module

    %% Click Events
    click UI_Module "https://github.com/retarduser404/typing-speed-analyzer/blob/main/tute.py"
    click Input_Handler "https://github.com/retarduser404/typing-speed-analyzer/blob/main/tute.py"
    click Game_Controller "https://github.com/retarduser404/typing-speed-analyzer/blob/main/tute.py"
    click Stats_Calc "https://github.com/retarduser404/typing-speed-analyzer/blob/main/tute.py"
    click Para_Loader "https://github.com/retarduser404/typing-speed-analyzer/blob/main/tute.py"
    click Score_Storage "https://github.com/retarduser404/typing-speed-analyzer/blob/main/tute.py"
    click Config "https://github.com/retarduser404/typing-speed-analyzer/blob/main/tute.py"
    click paras_txt "https://github.com/retarduser404/typing-speed-analyzer/blob/main/paras.txt"
    click scores_json "https://github.com/retarduser404/typing-speed-analyzer/blob/main/scores.json"
    click README "https://github.com/retarduser404/typing-speed-analyzer/blob/main/README.md"
    click LICENSE "https://github.com/retarduser404/typing-speed-analyzer/tree/main/LICENSE"

    %% Styles
    classDef ui fill:#D0E8FF,stroke:#3399FF,color:#000;
    classDef logic fill:#E0FFD8,stroke:#33CC33,color:#000;
    classDef persistence fill:#FFE5B4,stroke:#FF9900,color:#000;
    classDef config fill:#FFF5B4,stroke:#CCCC00,color:#000;
    classDef data fill:#FFF0F0,stroke:#CC0000,color:#000;
    classDef doc fill:#F0F0F0,stroke:#999999,color:#000;
    classDef external fill:#FFFFFF,stroke:#666666,color:#000;
