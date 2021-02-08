local grafana = import 'grafonnet/grafana.libsonnet';
local dashboard = grafana.dashboard;
local template = grafana.template;
local row = grafana.row;
local stat = grafana.statPanel;
local custom = grafana.customjson;
local prometheus = grafana.prometheus;

local gcp = import 'flavors/gcp.libsonnet';
local aws = import 'flavors/aws.libsonnet';
local azure = import 'flavors/azure.libsonnet';

local gcp_cost_panels = 
[
    gcp['e2-medium-prom'] + {gridPos: { h: 2, w: 4, x: 0, y: 10 }},

    gcp['e2-large-prom'] + {gridPos: { h: 2, w: 4, x: 4, y: 10 }},

    gcp['e2-xlarge-prom'] + {gridPos: { h: 2, w: 4, x: 8, y: 10 }},

    gcp['e2-highmem-2-prom'] + {gridPos: { h: 2, w: 4, x: 12, y: 10 }},

    gcp['e2-highcpu-4-prom'] + {gridPos: { h: 2, w: 4, x: 16, y: 10 }},

    gcp['e2-micro-prom'] + {gridPos: { h: 2, w: 4, x: 20, y: 10 }},
];

local aws_cost_panels = 
[
    aws['a1-medium-prom'] + {gridPos: { h: 2, w: 4, x: 0, y: 29 }},

    aws['a1-large-prom'] + {gridPos: { h: 2, w: 4, x: 4, y: 29 }},

    aws['a1-xlarge-prom'] + {gridPos: { h: 2, w: 4, x: 8, y: 29 }},

    aws['a1-2-xlarge-prom'] + {gridPos: { h: 2, w: 4, x: 12, y: 29 }},

    aws['t4g-micro-prom'] + {gridPos: { h: 2, w: 4, x: 16, y: 29 }},

    aws['t4g-nano-prom'] + {gridPos: { h: 2, w: 4, x: 20, y: 29 }},
];

local azure_cost_panels = 
[
  azure['b2s-prom'] + {gridPos: { h: 2, w: 4, x: 0, y: 48 }},

  azure['b2ms-prom'] + {gridPos: { h: 2, w: 4, x: 4, y: 48 }},

  azure['b4ms-prom'] + {gridPos: { h: 2, w: 4, x: 8, y: 48 }},

  azure['b1s-prom'] + {gridPos: { h: 2, w: 4, x: 12, y: 48 }},

  azure['b1ms-prom'] + {gridPos: { h: 2, w: 4, x: 16, y: 48 }},

  azure['a8-prom'] + {gridPos: { h: 2, w: 4, x: 20, y: 48 }},
];

dashboard.new(
    title='[Grafonnet] Cost Simulation Static',
    timepicker={},
    schemaVersion=26,
    time_from='now-6h',
    time_to='now',
    editable=true,
)
.addTemplate(
  grafana.template.datasource(
    name='PROMETHEUS_DS',
    current='Prometheus',
    query='prometheus',
  )
)

.addPanels(
    [
        stat.new(
        title=obj.title,
        datasource='Prometheus',
        transparent=true,
        )
        .addThresholds(
        [
            {
                color:'green',
                value:null
            },
            {
                color:'red',
                value:80
            }
        ]
        )
        .addTargets(
        [
            prometheus.target(
                expr=target.expr,
            )
            for target in obj.targets
        ],
        ) + { gridPos: obj.gridPos }
        for obj in gcp_cost_panels
    ],
)

.addPanels(
    [
        stat.new(
        title=obj.title,
        datasource='Prometheus',
        transparent=true,
        )
        .addThresholds(
        [
            {
                color:'green',
                value:null
            },
            {
                color:'red',
                value:80
            }
        ]
        )
        .addTargets(
        [
            prometheus.target(
                expr=target.expr,
            )
            for target in obj.targets
        ],
        ) + { gridPos: obj.gridPos }
        for obj in aws_cost_panels
    ],
)

.addPanels(
    [
        stat.new(
        title=obj.title,
        datasource='Prometheus',
        transparent=true,
        )
        .addThresholds(
        [
            {
                color:'green',
                value:null
            },
            {
                color:'red',
                value:80
            }
        ]
        )
        .addTargets(
        [
            prometheus.target(
                expr=target.expr,
            )
            for target in obj.targets
        ],
        ) + { gridPos: obj.gridPos }
        for obj in azure_cost_panels
    ],
)