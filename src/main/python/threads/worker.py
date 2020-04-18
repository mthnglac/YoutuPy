from PySide2.QtCore import QObject, Signal, QRunnable, Slot


class MyEmitter(QObject):
    # setting up custom signal
    done = Signal(str)
    """
    Defines the signals available from a running worker thread.
    Supported signals are:
    finished
        No data
    error
        `tuple` (exctype, value, traceback.format_exc() )
    result
        `object` data returned from processing, anything
    """
    finished = Signal()
    unfinished = Signal(str)
    error = Signal(tuple)
    result = Signal(object)
    progress = Signal(int)


class MyWorker(QRunnable):

    def __init__(self, fn, *args, **kwargs):
        super(MyWorker, self).__init__()
        self.emitter = MyEmitter()

        # Store constructor arguments (re-used for processing)
        self.fn = fn
        self.args = args
        self.kwargs = kwargs
        self.kwargs['progress_callback'] = self.emitter.progress

    # noinspection All
    @Slot()
    def run(self):
        try:
            result = self.fn(
                *self.args, **self.kwargs
            )
        except Exception as e:
            traceback.print_exc()
            exctype, value = sys.exc_info()[:2]
            self.emitter.error.emit((exctype, value, traceback.format_exc()))
        else:
            self.emitter.result.emit(result)
        finally:
            if result is not None:
                error_msg = "Error occured!"
                # print(result)
                # print(result.args)
                if type(result.args) == tuple:
                    if 'unavailable' in result.args[0]:
                        error_msg = result.args[0].split('said: ', 1)[1]
                    elif 'Unsupported' in result.args[0]:
                        error_msg = 'Unsupported URL'
                    self.emitter.unfinished.emit(error_msg)
                else:
                    self.emitter.unfinished.emit(result.args)
            else:
                self.emitter.finished.emit()
