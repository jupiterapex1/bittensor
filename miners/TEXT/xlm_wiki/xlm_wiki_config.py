axon:
  max_gradients: 100
  max_workers: 10
  use_upnpc: false
metagraph:
  stale_emit_filter: 10000
miner:
  accumulation_interval: 1
  apply_remote_gradients: false
  batch_size_train: 8
  config_file: null
  epoch_length: 10
  learning_rate: 0.01
  log_interval: 10
  momentum: 0.98
  n_epochs: 9223372036854775807
  name: xlm
  record_log: false
  root_dir: ~/.bittensor/miners/
  sync_interval: 100
neuron:
  modality: 0
nucleus:
  max_workers: 5
  queue_maxsize: 1000
  queue_timeout: 5
receptor:
  do_backoff: true
  max_backoff: 100
  pass_gradients: true
  timeout: 0.5
router:
  key_dim: 100
  stale_emit_filter: 10000
  topk: 10
subtensor:
  network: 'kusanagi'
synapse:
  n_heads: 16
  n_layers: 12
