import itertools
import wtforms_json

from wtforms import Form, IntegerField, BooleanField, FieldList

wtforms_json.init()


def monkey_patch_for_integer_field():
    """This function overrides BooleanField process_formdata in wtforms in order to
    support both integer and string data in json for integer field validation."""

    old_integer_process_formdata = IntegerField.process_formdata

    def integer_process_formdata(self, valuelist):
        old_integer_process_formdata(self, valuelist)
        if valuelist and valuelist[0] == 0:
            self.raw_data = ['0']

    IntegerField.process_formdata = integer_process_formdata


def monkey_patch_for_boolean_field():
    """This function overrides BooleanField process_formdata in wtforms and wtforms_json
    in order to support both boolean and string data in json for boolean field validation."""

    def boolean_process_formdata(self, valuelist):
        if not valuelist and self.default:
            return

        if valuelist and valuelist[0] is False:
            self.raw_data = ['false']

        if False not in self.false_values:
            self.false_values += (False,)
        if not valuelist or valuelist[0] in self.false_values:
            self.data = False
        else:
            self.data = True

    BooleanField.process_formdata = boolean_process_formdata


monkey_patch_for_integer_field()
monkey_patch_for_boolean_field()


class BaseForm(Form):
    @classmethod
    def from_request(cls, request):
        return cls.from_json(request.json)

    @classmethod
    def from_request_json(cls, request):
        return cls.from_json(request)

    def errors_first(self, count=None):
        return dict((name, f.errors[:count]) for name, f in self._fields.items() if f.errors)


class FieldList2(FieldList):
    def validate(self, form, extra_validators=tuple()):
        """
        this overrides FieldList.validate to make sure errors is same length as input
        """
        self.errors = []
        valid = True

        # Run validators on all entries within
        for subfield in self.entries:
            if not subfield.validate(form):
                self.errors.append(subfield.errors)
                valid = False
            else:
                self.errors.append({})

        chain = itertools.chain(self.validators, extra_validators)
        _ = self._run_validation_chain(form, chain)

        for error in self.errors:
            if len(error) > 0:
                valid = False
                break

        return valid
