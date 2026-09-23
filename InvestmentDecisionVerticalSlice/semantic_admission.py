from InvestmentDecisionVerticalSlice.validation import validate_semantic_output


def produce_and_admit_semantics(producer, request):
    output = producer.produce(request)
    validate_semantic_output(request, output)
    return output
