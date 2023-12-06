log_level = 'INFO'
load_from = None
resume_from = None
dist_params = dict(backend='nccl')
workflow = [('train', 1)]
checkpoint_config = dict(interval=10)
evaluation = dict(
    interval=10,
    metric=['PCK','NME','AUC','EPE'],
    key_indicator='PCK',
    gpu_collect=True,
    res_folder='results')
optimizer = dict(type='AdamW', lr=5e-4, betas=(0.9, 0.999), weight_decay=0.1,
                 constructor='LayerDecayOptimizerConstructor', 
                 paramwise_cfg=dict(
                                    num_layers=12, 
                                    layer_decay_rate=0.8,
                                    custom_keys={
                                            'bias': dict(decay_multi=0.),
                                            'pos_embed': dict(decay_mult=0.),
                                            'relative_position_bias_table': dict(decay_mult=0.),
                                            'norm': dict(decay_mult=0.)
                                            }
                                    )
                )

optimizer_config = dict(grad_clip=dict(max_norm=1., norm_type=2))

optimizer_config = dict(grad_clip=None)
# learning policy
lr_config = dict(
    policy='step',
    warmup='linear',
    warmup_iters=1000,
    warmup_ratio=0.001,
    step=[160, 180])
total_epochs = 200
log_config = dict(
    interval=50,
    hooks=[
        dict(type='TextLoggerHook'),
        dict(type='TensorboardLoggerHook')
    ])

channel_cfg = dict(
    num_output_channels=1,
    dataset_joints=1,
    dataset_channel=[
        [
            0,
        ],
    ],
    inference_channel=[
        0,
    ],
    max_kpt_num=100)

# model settings
model = dict(
    type='TransformerPoseTwoStage',
    Dino=True,
    pretrained='torchvision://resnet50',
    encoder_config=dict(type='ResNet', depth=50, out_indices=(3, )),
    keypoint_head=dict(
        type='TwoStageHead',
        in_channels=384,
        transformer=dict(
            type='TwoStageSupportRefineTransformer',
            d_model=256,
            nhead=8,
            num_encoder_layers=3,
            num_decoder_layers=3,
            dim_feedforward=2048,
            dropout=0.1,
            similarity_proj_dim=256,
            dynamic_proj_dim=128,
            activation="relu",
            normalize_before=False,
            return_intermediate_dec=True),
        share_kpt_branch=False,
        num_decoder_layer=3,
        with_heatmap_loss=True,
        heatmap_loss_weight=2.0,
        support_embedding_type="fixed",
        num_support=100,
        support_order_dropout=-1,
        positional_encoding=dict(
            type='SinePositionalEncoding', num_feats=128, normalize=True)),
    share_backbone=True,
    # training and testing settings
    train_cfg=dict(),
    test_cfg=dict(
        flip_test=False,
        post_process='default',
        shift_heatmap=True,
        modulate_kernel=11, 
        Dino=True
        ))

data_cfg = dict(
    image_size=[224, 224],
    heatmap_size=[64, 64],
    num_output_channels=channel_cfg['num_output_channels'],
    num_joints=channel_cfg['dataset_joints'],
    dataset_channel=channel_cfg['dataset_channel'],
    inference_channel=channel_cfg['inference_channel'])

train_pipeline = [
    dict(type='LoadImageFromFile'),
    dict(
        type='TopDownGetRandomScaleRotation', rot_factor=15,
        scale_factor=0.15),
    dict(type='TopDownAffineFewShot'),
    dict(type='ToTensor'),
    dict(
        type='NormalizeTensor',
        mean=[0.485, 0.456, 0.406],
        std=[0.229, 0.224, 0.225]),
    dict(type='TopDownGenerateTargetFewShot', sigma=2),
    dict(
        type='Collect',
        keys=['img', 'target', 'target_weight'],
        meta_keys=[
            'image_file', 'joints_3d', 'joints_3d_visible', 'center', 'scale',
            'rotation', 'bbox_score', 'flip_pairs', 'category_id'
        ]),
]

valid_pipeline = [
    dict(type='LoadImageFromFile'),
    dict(type='TopDownAffineFewShot'),
    dict(type='ToTensor'),
    dict(
        type='NormalizeTensor',
        mean=[0.485, 0.456, 0.406],
        std=[0.229, 0.224, 0.225]),
    dict(type='TopDownGenerateTargetFewShot', sigma=2),
    dict(
        type='Collect',
        keys=['img', 'target', 'target_weight'],
        meta_keys=[
            'image_file', 'center', 'scale', 'rotation', 'bbox_score',
            'flip_pairs', 'category_id'
        ]),
]

test_pipeline = valid_pipeline

# data_root = '/media/sonnguyen/DATA2/Study/superAI/Pose-for-Everything/tools/data/mp100/'
data_root = '/home/hslee/Projects/PoseforEverything1/data/mp100/'
data = dict(
    samples_per_gpu=16,
    workers_per_gpu=8,
    train=dict(
        type='TransformerPoseDataset',
        ann_file=f'{data_root}/annotations/mp100_split4_train.json',
        img_prefix=f'{data_root}/images/',
        # img_prefix=f'{data_root}',
        data_cfg=data_cfg,
        valid_class_ids=None,
        max_kpt_num=channel_cfg['max_kpt_num'],
        num_shots=1,
        pipeline=train_pipeline),
    val=dict(
        type='TransformerPoseDataset',
        ann_file=f'{data_root}/annotations/mp100_split4_val.json',
        img_prefix=f'{data_root}/images/',
        # img_prefix=f'{data_root}',
        data_cfg=data_cfg,
        valid_class_ids=None,
        max_kpt_num=channel_cfg['max_kpt_num'],
        num_shots=1,
        num_queries=15,
        num_episodes=100,
        pipeline=valid_pipeline),
    test=dict(
        type='TestPoseDataset',
        ann_file=f'{data_root}/annotations/mp100_split4_test.json',
        img_prefix=f'{data_root}/images/',
        # img_prefix=f'{data_root}',
        data_cfg=data_cfg,
        valid_class_ids=None,
        max_kpt_num=channel_cfg['max_kpt_num'],
        num_shots=1,
        num_queries=15,
        num_episodes=200,  # 200
        pck_threshold_list=[0.05, 0.10, 0.15, 0.2, 0.25],
        pipeline=test_pipeline),
)

shuffle_cfg = dict(interval=1)