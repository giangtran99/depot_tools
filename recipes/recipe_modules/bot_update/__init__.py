PYTHON_VERSION_COMPATIBILITY = 'PY3'

DEPS = [
    'depot_tools',
    'gclient',
    'gerrit',
    'gitiles',
    'gsutil',
    'recipe_engine/archive',
    'recipe_engine/buildbucket',
    'recipe_engine/context',
    'recipe_engine/commit_position',
    'recipe_engine/cv',
    'recipe_engine/json',
    'recipe_engine/led',
    'recipe_engine/milo',
    'recipe_engine/path',
    'recipe_engine/platform',
    'recipe_engine/properties',
    'recipe_engine/raw_io',
    'recipe_engine/runtime',
    'recipe_engine/step',
    'tryserver',
]

from recipe_engine.recipe_api import Property

PROPERTIES = {
  # Gerrit patches will have all properties about them prefixed with patch_.
  'deps_revision_overrides': Property(default={}),
  'fail_patch': Property(default=None, kind=str),

  '$depot_tools/bot_update': Property(
      help='Properties specific to bot_update module.',
      param_name='properties',
      default={},
  ),
}
