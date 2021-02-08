local grafana = import 'grafonnet/grafana.libsonnet';
local dashboard = grafana.dashboard;
local template = grafana.template;
local row = grafana.row;
local stat = grafana.statPanel;
local custom = grafana.customjson;

dashboard.new(
    title='[Grafonnet] Cost Simulation Dynamic',
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
.addTemplate(
    grafana.template.custom(
        name='interval',
        query='daily,weekly,monthly',
        current='daily',
    )
)
.addTemplate(
    grafana.template.custom(
        name='gcp',
        query='e2_medium,e2_large,e2_xlarge,e2_highmem_2,e2_highcpu_4,e2_micro',
        current='All',
        multi=true,
        includeAll=true,
    )
)
.addTemplate(
    grafana.template.custom(
        name='aws',
        query='a1_medium,a1_large,a1_xlarge,a1_2_xlarge,t4g_micro,t4g_nano',
        current='All',
        multi=true,
        includeAll=true,
    )
)
.addTemplate(
    grafana.template.custom(
        name='azure',
        query='b2s,b2ms,b4ms,b1s,b1ms,a8',
        current='All',
        multi=true,
        includeAll=true,
    )
)
.addPanels(
  [
    row.new(
      title='GCP Biling',
      showTitle=true,
    ) + { gridPos: {h: 1, w: 24, x: 0, y: 0} },
    row.new(
      title='AWS Biling',
      showTitle=true,
    ) + { gridPos: {h: 1, w: 24, x: 0, y: 4} },
    row.new(
      title='Azure Biling',
      showTitle=true,
    ) + { gridPos: {h: 1, w: 24, x: 0, y: 8} },
  ]
)
.addPanels(
    [
        stat.new(
            title='$interval gcp_$gcp',
            datasource='Rating-operator',
            transparent=true,
            repeat='gcp',
            repeatDirection='h',
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
                    target='/metrics/<metric>/<aggregator>',
                    data="{\"metric\": \"node_cost_simulation_gcp_$gcp\", \"aggregator\": \"$interval\"}",
                    type='table',
                )
            ],
        ) + {gridPos: { h: 3, w: 4, x: 0, y: 1 }},
    ],
)
.addPanels(
    [
        stat.new(
            title='$interval aws_$aws',
            datasource='Rating-operator',
            transparent=true,
            repeat='aws',
            repeatDirection='h',
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
                    target='/metrics/<metric>/<aggregator>',
                    data="{\"metric\": \"node_cost_simulation_aws_$aws\", \"aggregator\": \"$interval\"}",
                    type='table',
                )
            ],
        ) + {gridPos: { h: 3, w: 4, x: 0, y: 5 }},
    ],
)
.addPanels(
    [
        stat.new(
            title='$interval azure_$azure',
            datasource='Rating-operator',
            transparent=true,
            repeat='azure',
            repeatDirection='h',
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
                    target='/metrics/<metric>/<aggregator>',
                    data="{\"metric\": \"node_cost_simulation_aks_$azure\", \"aggregator\": \"$interval\"}",
                    type='table',
                )
            ],
        ) + {gridPos: { h: 3, w: 4, x: 0, y: 9 }},
    ],
)