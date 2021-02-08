local grafana = import 'grafonnet/grafana.libsonnet';
local dashboard = grafana.dashboard;
local template = grafana.template;
local row = grafana.row;
local stat = grafana.statPanel;
local custom = grafana.customjson;

local gcp = import 'flavors/gcp.libsonnet';
local aws = import 'flavors/aws.libsonnet';
local azure = import 'flavors/azure.libsonnet';

local gcp_cost_panels = 
[
    gcp['e2-medium-daily'] + {gridPos: { h: 2, w: 4, x: 0, y: 10 }},
    gcp['e2-medium-weekly'] + {gridPos: { h: 2, w: 4, x: 0, y: 12 }},
    gcp['e2-medium-monthly'] + {gridPos: { h: 2, w: 4, x: 0, y: 14 }},

    gcp['e2-large-daily'] + {gridPos: { h: 2, w: 4, x: 4, y: 10 }},
    gcp['e2-large-weekly'] + {gridPos: { h: 2, w: 4, x: 4, y: 12 }},
    gcp['e2-large-monthly'] + {gridPos: { h: 2, w: 4, x: 4, y: 14 }},

    gcp['e2-xlarge-daily'] + {gridPos: { h: 2, w: 4, x: 8, y: 10 }},
    gcp['e2-xlarge-weekly'] + {gridPos: { h: 2, w: 4, x: 8, y: 12 }},
    gcp['e2-xlarge-monthly'] + {gridPos: { h: 2, w: 4, x: 8, y: 14 }},

    gcp['e2-highmem-2-daily'] + {gridPos: { h: 2, w: 4, x: 12, y: 10 }},
    gcp['e2-highmem-2-weekly'] + {gridPos: { h: 2, w: 4, x: 12, y: 12 }},
    gcp['e2-highmem-2-monthly'] + {gridPos: { h: 2, w: 4, x: 12, y: 14 }},

    gcp['e2-highcpu-4-daily'] + {gridPos: { h: 2, w: 4, x: 16, y: 10 }},
    gcp['e2-highcpu-4-weekly'] + {gridPos: { h: 2, w: 4, x: 16, y: 12 }},
    gcp['e2-highcpu-4-monthly'] + {gridPos: { h: 2, w: 4, x: 16, y: 14 }},

    gcp['e2-micro-daily'] + {gridPos: { h: 2, w: 4, x: 20, y: 10 }},
    gcp['e2-micro-weekly'] + {gridPos: { h: 2, w: 4, x: 20, y: 12 }},
    gcp['e2-micro-monthly'] + {gridPos: { h: 2, w: 4, x: 20, y: 14 }},
];

local aws_cost_panels = 
[
    aws['a1-medium-daily'] + {gridPos: { h: 2, w: 4, x: 0, y: 29 }},
    aws['a1-medium-weekly'] + {gridPos: { h: 2, w: 4, x: 0, y: 31 }},
    aws['a1-medium-monthly'] + {gridPos: { h: 2, w: 4, x: 0, y: 33 }},

    aws['a1-large-daily'] + {gridPos: { h: 2, w: 4, x: 4, y: 29 }},
    aws['a1-large-weekly'] + {gridPos: { h: 2, w: 4, x: 4, y: 31 }},
    aws['a1-large-monthly'] + {gridPos: { h: 2, w: 4, x: 4, y: 33 }},

    aws['a1-xlarge-daily'] + {gridPos: { h: 2, w: 4, x: 8, y: 29 }},
    aws['a1-xlarge-weekly'] + {gridPos: { h: 2, w: 4, x: 8, y: 31 }},
    aws['a1-xlarge-monthly'] + {gridPos: { h: 2, w: 4, x: 8, y: 33 }},

    aws['a1-2-xlarge-daily'] + {gridPos: { h: 2, w: 4, x: 12, y: 29 }},
    aws['a1-2-xlarge-weekly'] + {gridPos: { h: 2, w: 4, x: 12, y: 31 }},
    aws['a1-2-xlarge-monthly'] + {gridPos: { h: 2, w: 4, x: 12, y: 33 }},

    aws['t4g-micro-daily'] + {gridPos: { h: 2, w: 4, x: 16, y: 29 }},
    aws['t4g-micro-weekly'] + {gridPos: { h: 2, w: 4, x: 16, y: 31 }},
    aws['t4g-micro-monthly'] + {gridPos: { h: 2, w: 4, x: 16, y: 33 }},

    aws['t4g-nano-daily'] + {gridPos: { h: 2, w: 4, x: 20, y: 29 }},
    aws['t4g-nano-weekly'] + {gridPos: { h: 2, w: 4, x: 20, y: 31 }},
    aws['t4g-nano-monthly'] + {gridPos: { h: 2, w: 4, x: 20, y: 33 }},
];

local azure_cost_panels = 
[
  azure['b2s-daily'] + {gridPos: { h: 2, w: 4, x: 0, y: 48 }},
  azure['b2s-weekly'] + {gridPos: { h: 2, w: 4, x: 0, y: 50 }},
  azure['b2s-monthly'] + {gridPos: { h: 2, w: 4, x: 0, y: 52 }},

  azure['b2ms-daily'] + {gridPos: { h: 2, w: 4, x: 4, y: 48 }},
  azure['b2ms-weekly'] + {gridPos: { h: 2, w: 4, x: 4, y: 50 }},
  azure['b2ms-monthly'] + {gridPos: { h: 2, w: 4, x: 4, y: 52 }},

  azure['b4ms-daily'] + {gridPos: { h: 2, w: 4, x: 8, y: 48 }},
  azure['b4ms-weekly'] + {gridPos: { h: 2, w: 4, x: 8, y: 50 }},
  azure['b4ms-monthly'] + {gridPos: { h: 2, w: 4, x: 8, y: 52 }},

  azure['b1s-daily'] + {gridPos: { h: 2, w: 4, x: 12, y: 48 }},
  azure['b1s-weekly'] + {gridPos: { h: 2, w: 4, x: 12, y: 50 }},
  azure['b1s-monthly'] + {gridPos: { h: 2, w: 4, x: 12, y: 52 }},

  azure['b1ms-daily'] + {gridPos: { h: 2, w: 4, x: 16, y: 48 }},
  azure['b1ms-weekly'] + {gridPos: { h: 2, w: 4, x: 16, y: 50 }},
  azure['b1ms-monthly'] + {gridPos: { h: 2, w: 4, x: 16, y: 52 }},

  azure['a8-daily'] + {gridPos: { h: 2, w: 4, x: 20, y: 48 }},
  azure['a8-weekly'] + {gridPos: { h: 2, w: 4, x: 20, y: 50 }},
  azure['a8-monthly'] + {gridPos: { h: 2, w: 4, x: 20, y: 52 }},
];

local aws_nbinstance_panel = [
  aws['a1-medium-instance'] + {gridPos: { h: 3, w: 4, x: 0, y: 26 }},
  aws['a1-large-instance'] + {gridPos: { h: 3, w: 4, x: 4, y: 26 }},
  aws['a1-xlarge-instance'] + {gridPos: { h: 3, w: 4, x: 8, y: 26 }},
  aws['a1-2-xlarge-instance'] + {gridPos: { h: 3, w: 4, x: 12, y: 26 }},
  aws['t4g-micro-instance'] + {gridPos: { h: 3, w: 4, x: 16, y: 26 }},
  aws['t4g-nano-instance'] + {gridPos: { h: 3, w: 4, x: 20, y: 26 }},
];

local gcp_nbinstance_panel = [
  gcp['e2-medium-instance'] + {gridPos: { h: 3, w: 4, x: 0, y: 5 }},
  gcp['e2-large-instance'] + {gridPos: { h: 3, w: 4, x: 4, y: 5 }},
  gcp['e2-xlarge-instance'] + {gridPos: { h: 3, w: 4, x: 8, y: 5 }},
  gcp['e2-highmem-2-instance'] + {gridPos: { h: 3, w: 4, x: 12, y: 5 }},
  gcp['e2-highcpu-4-instance'] + {gridPos: { h: 3, w: 4, x: 16, y: 5 }},
  gcp['e2-micro-instance'] + {gridPos: { h: 3, w: 4, x: 20, y: 5 }},
];

local azure_nbinstance_panel = [
  azure['b2s-instance'] + {gridPos: { h: 3, w: 4, x: 0, y: 45 }},
  azure['b2ms-instance'] + {gridPos: { h: 3, w: 4, x: 4, y: 45 }},
  azure['b4ms-instance'] + {gridPos: { h: 3, w: 4, x: 8, y: 45 }},
  azure['b1s-instance'] + {gridPos: { h: 3, w: 4, x: 12, y: 45 }},
  azure['b1ms-instance'] + {gridPos: { h: 3, w: 4, x: 16, y: 45 }},
  azure['a8-instance'] + {gridPos: { h: 3, w: 4, x: 20, y: 45 }},
];

dashboard.new(
    title='[Grafonnet] Cost Simulation',
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
    row.new(
      title='GCP Biling',
      showTitle=true,
    ) + { gridPos: {h: 1, w: 24, x: 0, y: 4} },
    row.new(
      title='AWS Biling',
      showTitle=true,
    ) + { gridPos: {h: 1, w: 24, x: 0, y: 25} },
    row.new(
      title='Azure Biling',
      showTitle=true,
    ) + { gridPos: {h: 1, w: 24, x: 0, y: 44} },
  ] + [
    stat.new(
      title=obj.title,
      datasource='Rating-operator',
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
        custom.target(
          target=target.target,
          data=target.data,
          type=target.type,
        )
        for target in obj.targets
      ],
    ) + { gridPos: obj.gridPos }
    for obj in gcp_cost_panels
  ] + [
    stat.new(
      title=obj.title,
      datasource='Rating-operator',
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
        custom.target(
          target=target.target,
          data=target.data,
          type=target.type,
        )
        for target in obj.targets
      ],
    ) + { gridPos: obj.gridPos }
    for obj in aws_cost_panels
  ] + [
      stat.new(
      title=obj.title,
      datasource='Rating-operator',
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
        custom.target(
          target=target.target,
          data=target.data,
          type=target.type,
        )
        for target in obj.targets
      ],
    ) + { gridPos: obj.gridPos }
    for obj in azure_cost_panels
  ] ,
)
.addPanels(
  [
    stat.new(
      title=obj.title,
      datasource='Rating-operator',
      transparent=true,
      reducerFunction='lastNotNull',
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
          target=target.target,
          data=target.data,
          type=target.type,
        )
        for target in obj.targets
      ],
    ) + { gridPos: obj.gridPos }
    for obj in aws_nbinstance_panel
  ] + [
    stat.new(
      title=obj.title,
      datasource='Rating-operator',
      transparent=true,
      reducerFunction='lastNotNull',
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
        custom.target(
          target=target.target,
          data=target.data,
          type=target.type,
        )
        for target in obj.targets
      ],
    ) + { gridPos: obj.gridPos }
    for obj in gcp_nbinstance_panel
  ] + [
    stat.new(
      title=obj.title,
      datasource='Rating-operator',
      transparent=true,
      reducerFunction='lastNotNull',
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
          target=target.target,
          data=target.data,
          type=target.type,
        )
        for target in obj.targets
      ],
    ) + { gridPos: obj.gridPos }
    for obj in azure_nbinstance_panel
  ],
)

