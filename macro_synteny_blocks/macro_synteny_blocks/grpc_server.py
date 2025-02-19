# dependencies
import grpc
from grpc.experimental import aio
# module
from macro_synteny_blocks.proto.macrosyntenyblocks_service.v1 import macrosyntenyblocks_pb2
from macro_synteny_blocks.proto.macrosyntenyblocks_service.v1 import macrosyntenyblocks_pb2_grpc


class MacroSyntenyBlocks(macrosyntenyblocks_pb2_grpc.MacroSyntenyBlocksServicer):

  def __init__(self, handler):
    self.handler = handler

  async def Compute(self, request, context):
    # required parameters
    chromosome = request.chromosome
    matched = request.matched
    intermediate = request.intermediate
    # optional parameters
    mask = request.mask or None
    targets = request.targets or None
    metrics = request.optionalMetrics or None
    chromosome_genes = request.chromosomeGenes or None
    chromosome_length = request.chromosomeLength or None
    try:
      chromosome, matched, intermediate, mask, targets, metrics, chromosome_genes, chromosome_length = \
        self.handler.parseArguments(chromosome, matched, intermediate, mask, targets, metrics, chromosome_genes, chromosome_length)
    except:
      # raise a gRPC INVALID ARGUMENT error
      await context.abort(grpc.StatusCode.INVALID_ARGUMENT, 'Required arguments are missing or given arguments have invalid values')
    blocks = await self.handler.process(chromosome, matched, intermediate, mask, targets, metrics, chromosome_genes, chromosome_length)
    return macrosyntenyblocks_pb2.MacroSyntenyBlocksComputeReply(blocks=blocks)


async def run_grpc_server(host, port, handler):
  server = aio.server()
  server.add_insecure_port(f'{host}:{port}')
  servicer = MacroSyntenyBlocks(handler)
  macrosyntenyblocks_pb2_grpc.add_MacroSyntenyBlocksServicer_to_server(servicer, server)
  await server.start()
  await server.wait_for_termination()
