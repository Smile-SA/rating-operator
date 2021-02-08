local grafana = import 'grafonnet/grafana.libsonnet';
local dashboard = grafana.dashboard;
local template = grafana.template;
local graph = grafana.graphPanel;
local stat = grafana.statPanel;
local gauge = grafana.gaugePanel;
local custom = grafana.customjson;

dashboard.new(
    title='[Grafonnet] Default Dashboard',
    timepicker={},
    schemaVersion=26,
    time_from='now-6h',
    time_to='now',
    editable=true,
)
.addTemplate(
  grafana.template.datasource(
    name='Rating-operator',
    current='Rating-operator',
    query='JSON',
    hide=true,
  )
)
.addPanels(
    [
        graph.new(
            title='Rating-operator CPU Usage',
            datasource='Rating-operator',
            transparent=true,
        )
        .addTargets(
            [
                custom.target(
                    target='/namespaces/<namespace>/metrics/<metric>/rating',
                    data="{\"metric\": \"pods_usage_cpu\", \"namespace\": \"rating-operator\"}",
                    type='timeseries',
                ) 
            ],
        ) + { gridPos: {h: 7, w: 12, x: 0, y: 0} }
    ],
)
.addPanels(
    [
        graph.new(
            title='Rating-operator RAM Usage',
            datasource='Rating-operator',
            transparent=true,
        )
        .addTargets(
            [
                custom.target(
                    target='/namespaces/<namespace>/metrics/<metric>/rating',
                    data="{\"metric\": \"pods_usage_memory\", \"namespace\": \"rating-operator\"}",
                    type='timeseries',
                ) 
            ],
        ) + { gridPos: {h: 7, w: 12, x: 12, y: 0} }
    ],
)
.addPanels(
    [
        stat.new(
            title='Oldest Prometheus data',
            datasource='Rating-operator',
            transparent=true,
            reducerFunction='last',
            fields='price',
            unit='dateTimeAsIso'
        )
        .addTargets(
            [
                custom.target(
                    target='/metrics/<metric>/rating',
                    data="{\"metric\": \"prometheus_oldest_data\"}",
                    type='table',
                ) 
            ],
        ) + { gridPos: {h: 2, w: 12, x: 0, y: 7} }
    ],
)
.addPanels(
    [
        stat.new(
            title='Oldest rated data',
            datasource='Rating-operator',
            transparent=true,
            allValues=true,
            fields='min',
            unit='dateTimeFromNow'
        )
        .addTargets(
            [
                custom.target(
                    target='/rated/frames/oldest',
                    type='table',
                    data='',
                ) 
            ],
        ) + { gridPos: {h: 2, w: 12, x: 12, y: 7} }
    ],
)
.addPanels(
    [
        graph.new(
            title='Prometheus storage (GB)',
            datasource='Rating-operator',
            staircase=true,
            transparent=true,
        )
        .addTargets(
            [
                custom.target(
                    target='/metrics/<metric>/ratio',
                    data="{\"metric\": \"prometheus_storage_size\"}",
                    type='table',
                ) 
            ],
        ) + { gridPos: {h: 5, w: 12, x: 0, y: 9} }
    ],
)
.addPanels(
    [
        graph.new(
            title='Rating storage (GB)',
            datasource='Rating-operator',
            transparent=true,
        )
        .addTargets(
            [
                custom.target(
                    target='/metrics/<metric>/ratio',
                    data="{\"metric\": \"rating_storage_size\"}",
                    type='table',
                ) 
            ],
        ) + { gridPos: {h: 5, w: 12, x: 12, y: 9} }
    ],
)
/*
.addPanels(
    [
        gauge.new(
            title='CPU vs RAM on nodes',
            datasource='Rating-operator',
            transparent=true,
            unit=null,
            max=1,
        )
        .addThresholds(
            [
                {
                color:'green',
                value:null
                },
            ]
        )
        .addTargets(
            [
                custom.target(
                    target='/nodes/metrics/<metric>/rating',
                    data="{\"metric\": \"node_cpu_memory_ratio\"}",
                    type='timeseries',
                ) 
            ],
        ) + { gridPos: {h: 4, w: 24, x: 0, y: 14} }
    ],
)
.addPanels(
    [
        graph.new(
            title='CPU vs RAM ratio',
            datasource='Rating-operator',
            transparent=true,
        )
        .addTargets(
            [
                custom.target(
                    target='/metrics/<metric>/ratio',
                    data="{\"metric\": \"node_cpu_memory_ratio\"}",
                    type='table',
                )
            ],
        ) + { gridPos: {h: 6, w: 24, x: 0, y: 18} }
    ],
)
*/