local grafana = import 'grafonnet/grafana.libsonnet';
local dashboard = grafana.dashboard;
local template = grafana.template;
local graph = grafana.graphPanel;
local gauge = grafana.gaugePanel;
local custom = grafana.customjson;

dashboard.new(
    title='[Grafonnet] Application Performance',
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
        gauge.new(
            title='CPU vs RAM ratio per instance (more than 1, CPU is preferred)',
            description='(more than 1, CPU is preferred)',
            datasource='Rating-operator',
            unit=null,
            max=1,
            transparent=true,
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
        ) + { gridPos: {h: 5, w: 24, x: 0, y: 0} }
    ],
)
.addPanels(
    [
        graph.new(
            title='CPU vs RAM ratio (more than 1, CPU is preferred)',
            description='(more than 1, CPU is preferred)',
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
        ) + { gridPos: {h: 6, w: 24, x: 0, y: 5} }
    ],
)
.addPanels(
    [
        graph.new(
            title='STORAGE vs RAM ratio (more than 1, STORAGE is preferred)',
            description='(more than 1, STORAGE is preferred)',
            datasource='Rating-operator',
            transparent=true,
        )
        .addTargets(
            [
                custom.target(
                    target='/metrics/<metric>/ratio',
                    data="{\"metric\": \"storage_ram_ratio\"}",
                    type='table',
                )
            ],
        ) + { gridPos: {h: 6, w: 24, x: 0, y: 11} }
    ],
)
.addPanels(
    [
        graph.new(
            title='Resource consumption',
            description='RAM in GB, CPU in milicore',
            datasource='Rating-operator',
            transparent=true,
        )
        .addTargets(
            [
                custom.target(
                    target='/metrics/rating',
                    type='timeseries',
                    data=''
                )
            ],
        ) + { gridPos: {h: 7, w: 24, x: 0, y: 17} }
    ],
)
