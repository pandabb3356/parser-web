class BaseTask(object):
    app = None
    ctx = None

    def __init__(self, perform_func=None):
        self._perform = perform_func

    def _before_perform(self):
        if not self.app:
            from web import create_app

            app = create_app()
            self.app = app

        self.ctx = self.app.test_request_context('/')
        self.ctx.push()

    def _after_perform(self):
        self.ctx.pop()

    def _perform_success(self):
        pass

    def _perform_failure(self):
        pass

    def perform(self, *args):
        success = False
        try:
            self._before_perform()
            if self._perform is not None:
                self._perform(*args)
            success = True
        finally:
            if success:
                self._perform_success()
            else:
                self._perform_failure()
            self._after_perform()
