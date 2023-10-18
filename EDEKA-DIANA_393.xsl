
<xsl:stylesheet version="1.0" xmlns:xsl="http://www.w3.org/1999/XSL/Transform" xmlns:date="http://exslt.org/dates-and-times" xmlns:exsl="http://exslt.org/common" extension-element-prefixes="date exsl">
	<xsl:import href="EDIFACT-xml2edi.xsl"/>
	<xsl:output method="text" indent="yes" encoding="utf-8"/>

	<!--Made By Andris Kopmanis|Edisoft Latvia SIA|02.07.2020|-->

	<xsl:variable name="currency" select="normalize-space(Document-Invoice/Invoice-Header/InvoiceCurrency)"/>
	<xsl:variable name="remarks" select="normalize-space(Document-Invoice/Invoice-Header/Remarks)"/>
	<!-- Root template -->
	<xsl:template match="/">
		
		<xsl:variable name="processed_doc_tmp">
			<xsl:apply-templates mode="interchange" select="/Document-Invoice"/>
		</xsl:variable>
		
		<xsl:apply-templates select="exsl:node-set($processed_doc_tmp)/child::*"/>
	</xsl:template>
	<!-- Invoice -->

	<xsl:template mode="interchange" match="Document-Invoice">
		<!-- Process the document -->
		<xsl:variable name="processed_doc_tmp">
			<xsl:apply-templates mode="message" select="."/>
		</xsl:variable>
		<xsl:variable name="processed_doc" select="exsl:node-set($processed_doc_tmp)"/>



		
		<xsl:copy-of select="$processed_doc"/>
		<!-- The interchange envelope (end) -->
		<segment tag="UNZ">
			<element>
				<xsl:value-of select="'3'"/>
			</element>
			<element>
				<!-- Number of messages or functional groups (if present) -->
				<xsl:value-of select="normalize-space(Invoice-Header/InvoiceNumber)"/>
			</element>
		</segment>
	</xsl:template>
	<!-- Invoice -->
	<xsl:template mode="message" match="Document-Invoice">
		<!-- Process the document -->
		<xsl:variable name="processed_doc_tmp">
			<xsl:apply-templates mode="segments" select="."/>
		</xsl:variable>
		<xsl:variable name="processed_doc" select="exsl:node-set($processed_doc_tmp)"/>

	
		<segment tag="UNH">
			<element>
		
				<xsl:value-of select="'3'"/>
			</element>
			<element>
				<subelement>
					<xsl:text>INVOIC</xsl:text>
				</subelement>
				<subelement>
					<xsl:text>D</xsl:text>
				</subelement>
				<subelement>
					<xsl:text>01B</xsl:text>
				</subelement>
				<subelement>
					<xsl:text>UN</xsl:text>
				</subelement>
				<subelement>
					<xsl:text>EAN010</xsl:text>
				</subelement>
			</element>
		</segment>
		<!-- Main content (has only the beginning of the message envelope) -->
		<xsl:copy-of select="$processed_doc"/>
		<!-- Message envelope (end) -->
		<!-- UNT Message trailer -->
		<segment tag="UNT">
			<element>
				<!-- Number of segments between UNH and UNT (inclusive) -->
				<xsl:value-of select="count($processed_doc/segment) + 2"/>
				<!-- Or: count($processed_doc/child::*) + 1 -->
			</element>
			<element>
				<!-- Sender's unique message reference (OrderNumber) -->
				<!-- xsl:value-of select="normalize-space(Order-Header/OrderNumber)"  -->
				<xsl:value-of select="'3'"/>
			</element>
		</segment>
	</xsl:template>

	<!-- Invoice -->
	<xsl:template mode="segments" match="Document-Invoice">
		<!--PTG Management and OTHERS D01B Format Abroad partners-->
		<!-- Header -->
		<!-- BGM BEGINNING OF MESSAGE -->
		<segment tag="BGM">
			<!-- C002  DOCUMENT/MESSAGE NAME (C) -->
			<element>
				<!-- 1001   Document/message name, coded (C  an..3) -->
				<subelement>
					<xsl:text>393</xsl:text>

					<!-- 388 Tax invoice,  380 Commercial Invoice -->
				</subelement>
				<!-- 1131   Code list qualifier (C  an..3) -->
				<subelement/>
				<!-- 3055   Code list responsible agency, coded (C  an..3) -->
				<subelement/>
				<!-- 1000   Document/message name (C  an..35) -->
				<!-- E.g., INVOIC -->
				<subelement/>
			</element>
			<!-- 1004  DOCUMENT/MESSAGE NUMBER (C  an..35) -->
			<element>
				<xsl:value-of select="substring(normalize-space(Invoice-Header/InvoiceNumber), 1, 35)"/>
			</element>
			<!-- 1225  MESSAGE FUNCTION, CODED (C  an..3) -->
			<element>
				<xsl:text>9</xsl:text>
				<!-- 9 Original -->
			</element>
			<!-- 4343  RESPONSE TYPE, CODED (C  an..3) -->
			<!-- AB Message acknowledgement, NA No acknowledgement needed -->
			<element/>
		</segment>

		<segment tag="DTM">
			<!-- C507  DATE/TIME/PERIOD (M) -->
			<element>
				<!-- 2005   Date/time/period qualifier (M  an..3) -->
				<subelement>
					<xsl:text>137</xsl:text>
					<!-- 325 Tax period  	Period a tax rate/tax amount etc. is applicable. 	
GS1 Description: A period which is designated by tax authorities, e.g. VAT period. -->
				</subelement>
				<!-- 2380   Date/time/period (C  an..35) -->
				<subelement>

					<!-- Original value of EDIFACT D01B |Andris Kopmanis|-->

					<!--<xsl:value-of select="translate(normalize-space(Invoice-Header/InvoiceDate), '-', '')"/>-->

					<xsl:value-of select="translate(normalize-space(Invoice-Header/InvoiceDate), '-', '')"/>
				</subelement>
				<!-- 2379   Date/time/period format qualifier (C  an..3) -->
				<subelement>
					<xsl:text>102</xsl:text>
					<!-- Date/time/period format qualifier: CCYYMMDD -->
				</subelement>
			</element>
		</segment>

	
		<!-- RFF REFERENCE -->
		<segment tag="RFF">
			<element>
				<subelement>
					<xsl:text>CT</xsl:text>
					<!-- ON Order number (purchase) -->
				</subelement>
				<subelement>
					<xsl:value-of select="substring(normalize-space(Invoice-Header/InvoiceNumber), 1, 35)"/>
				</subelement>
			</element>
		</segment>

		<!-- Segment group 2: NAD-LOC-FII-SG3-SG4-SG5 -->
		<!-- NAD NAME AND ADDRESS -->
		<segment tag="NAD">
			<!-- 3035  PARTY QUALIFIER (M  an..3) -->
			<element>
				<xsl:text>SU</xsl:text>
				<!-- SE Seller -->
			</element>
			<!-- C082  PARTY IDENTIFICATION DETAILS (C) -->
			<element>
				<!-- 3039   Party id. identification (M  an..35) -->
				<subelement>
					<xsl:value-of select="normalize-space(Invoice-Parties/Seller/ILN)"/>
				</subelement>
				<!-- 1131   Code list qualifier (C  an..3) -->
				<subelement/>
				<!-- 3055   Code list responsible agency, coded (C  an..3) -->
				<subelement>
					<!--  9 EAN -->
					<!-- 91 Assigned by seller or seller's agent -->
					<!-- 92 Assigned by buyer or buyer's agent -->
					<xsl:text>9</xsl:text>
				</subelement>
			</element>
		</segment>

		<!-- NAD NAME AND ADDRESS -->
		<segment tag="NAD">
			<!-- 3035  PARTY QUALIFIER (M  an..3) -->
			<element>
				<xsl:text>CPE</xsl:text>
				<!-- BY Buyer -->
			</element>
			<!-- C082  PARTY IDENTIFICATION DETAILS (C) -->
			<element>
				<!-- 3039   Party id. identification (M  an..35) -->
				<subelement>
					<xsl:value-of select="normalize-space(Document-Parties/Receiver/ILN)"/>
				</subelement>
				<!-- 1131   Code list qualifier (C  an..3) -->
				<subelement/>
				<!-- 3055   Code list responsible agency, coded (C  an..3) -->
				<subelement>
					<!--  9 EAN -->
					<!-- 91 Assigned by seller or seller's agent -->
					<!-- 92 Assigned by buyer or buyer's agent -->
					<xsl:text>9</xsl:text>
				</subelement>
			</element>
		</segment>

		<segment tag="NAD">
			<!-- 3035  PARTY QUALIFIER (M  an..3) -->
			<element>
				<xsl:text>PR</xsl:text>
				<!--  	Ordered by Party who issued an order. -->
			</element>
			<!-- C082  PARTY IDENTIFICATION DETAILS (C) -->
			<element>
				<!-- 3039   Party id. identification (M  an..35) -->
				<subelement>
					<xsl:value-of select="Invoice-Parties/Payer/ILN"/>
				</subelement>
				<!-- 1131   Code list qualifier (C  an..3) -->
				<subelement/>
				<!-- 3055   Code list responsible agency, coded (C  an..3) -->
				<subelement>
					<!--  9 EAN -->
					<!-- 91 Assigned by seller or seller's agent -->
					<!-- 92 Assigned by buyer or buyer's agent -->
					<xsl:text>9</xsl:text>
				</subelement>
			</element>
			<element/>
		</segment>

				<segment tag="NAD">
			<!-- 3035  PARTY QUALIFIER (M  an..3) -->
			<element>
				<xsl:text>PE</xsl:text>
				<!--  	Ordered by Party who issued an order. -->
			</element>
			<!-- C082  PARTY IDENTIFICATION DETAILS (C) -->
			<element>
				<!-- 3039   Party id. identification (M  an..35) -->
				<subelement>
					<xsl:value-of select="normalize-space(Invoice-Parties/Seller/ILN)"/>
				</subelement>
				<!-- 1131   Code list qualifier (C  an..3) -->
				<subelement/>
				<!-- 3055   Code list responsible agency, coded (C  an..3) -->
				<subelement>
					<!--  9 EAN -->
					<!-- 91 Assigned by seller or seller's agent -->
					<!-- 92 Assigned by buyer or buyer's agent -->
					<xsl:text>9</xsl:text>
				</subelement>
			</element>
			<element/>
		</segment>

		<!-- Tax-Summary-Line -->
		<segment tag="TAX">
			<!-- 5283  DUTY/TAX/FEE FUNCTION QUALIFIER (M  an..3) -->
			<element>
				<xsl:text>7</xsl:text>
				<!-- 7 Tax -->
			</element>
			<!-- C241  DUTY/TAX/FEE TYPE (C) -->
			<element>
				<!-- 5153   Duty/tax/fee type, coded (C  an..3) -->
				<subelement>
					<xsl:text>VAT</xsl:text>
					<!-- VAT -->
				</subelement>
				<!-- 1131   Code list qualifier (C  an..3) -->
				<!-- 3055   Code list responsible agency, coded (C  an..3) -->
				<!-- 5152   Duty/tax/fee type (C  an..35) -->
			</element>
			<!-- C533  DUTY/TAX/FEE ACCOUNT DETAIL -->
			<element/>
			<!-- 5286  DUTY/TAX/FEE ASSESSMENT BASIS (C  an..15) -->
			<element>
				<!--<xsl:value-of select="format-number(Invoice-Summary/Tax-Summary/Tax-Summary-Line/TaxableAmount, '0.00')"/>-->
			</element>

			<element>

				<subelement>
				</subelement>

				<subelement>
				</subelement>
				<subelement>
				</subelement>
				<subelement>
				<xsl:text>7</xsl:text>
				</subelement>
			</element>
			<element>
			<xsl:text>S</xsl:text>
			</element>
		</segment>


		<!-- NAD NAME AND ADDRESS -->
		<segment tag="CUX">
			<!-- C504  CURRENCY DETAILS (C) -->
			<element>
				<!-- 6347   Currency details qualifier (M  an..3) -->
				<subelement>
					<xsl:text>2</xsl:text>
					<!-- 2 Reference currency -->
				</subelement>
				<!-- 6345   Currency, coded (C  an..3) -->
				<subelement>
					<!--				<xsl:choose>
					<xsl:when test="$currency='CZK'">
						<xsl:value-of select="''"/>
					</xsl:when>
					<xsl:otherwise>-->
					<xsl:value-of select="$currency"/>
					<!--					</xsl:otherwise>
				</xsl:choose>-->
				</subelement>
				<!-- 6343   Currency qualifier (C  an..3) -->
				<subelement>
					<xsl:text>4</xsl:text>
					<!-- 4 Invoicing currency -->
				</subelement>
				<!-- 6348   Currency rate base (C  n..4) -->
				<subelement/>
			</element>
		</segment>

		<!--Processes Invoice Lines-->
		<xsl:apply-templates select="Invoice-Lines/Line/Line-Item"/>
		<!-- Summary section -->
		<!--UNS Section control-->
		<segment tag="UNS">
			<!--0081  SECTION IDENTIFICATION (M  a1)-->
			<element>
				<xsl:text>S</xsl:text>
			</element>
		</segment>


		<segment tag="MOA">
			<element>
				<subelement>
					<xsl:text>86</xsl:text>
				</subelement>
				<subelement>
					<xsl:value-of select="format-number(Invoice-Summary/TotalNetAmount, '0.00')"/>
				</subelement>
				<subelement/>
				<subelement/>
				<subelement/>
			</element>
		</segment>

		<!-- MOA Monetary amount -->
		<segment tag="MOA">
			<!-- C516  MONETARY AMOUNT (M) -->
			<element>
				<!-- 5025   Monetary amount type qualifier (M  an..3) -->
				<subelement>
					<xsl:text>124</xsl:text>
					<!-- 79 Total line items amount -->
				</subelement>
				<!-- 5004   Monetary amount (C  n..18) -->
				<subelement>
					<xsl:value-of select="format-number(Invoice-Summary/TotalTaxAmount, '0.00')"/>
				</subelement>
				<!-- 6345   Currency, coded (C  an..3) -->
				<subelement/>
				<!-- 6343   Currency qualifier (C  an..3) -->
				<subelement/>
				<!-- 4405   Status, coded (C  an..3) -->
				<subelement/>
			</element>
		</segment>
			<segment tag="MOA">
			<!-- C516  MONETARY AMOUNT (M) -->
			<element>
				<!-- 5025   Monetary amount type qualifier (M  an..3) -->
				<subelement>
					<xsl:text>125</xsl:text>
					<!-- 79 Total line items amount -->
				</subelement>
				<!-- 5004   Monetary amount (C  n..18) -->
				<subelement>
					<xsl:value-of select="Invoice-Summary/TotalNetAmount"/>
				</subelement>
				<!-- 6345   Currency, coded (C  an..3) -->
				<subelement/>
				<!-- 6343   Currency qualifier (C  an..3) -->
				<subelement/>
				<!-- 4405   Status, coded (C  an..3) -->
				<subelement/>
			</element>
		</segment>
		<!-- MOA Monetary amount -->
		<segment tag="MOA">
			<!-- C516  MONETARY AMOUNT (M) -->
			<element>
				<!-- 5025   Monetary amount type qualifier (M  an..3) -->
				<subelement>
					<xsl:text>9</xsl:text>
					<!-- 125 Taxable amount -->
				</subelement>
				<!-- 5004   Monetary amount (C  n..18) -->
				<subelement>
					<xsl:value-of select="Invoice-Summary/TotalNetAmount"/>
				</subelement>
				<!-- 6345   Currency, coded (C  an..3) -->
				<subelement/>
				<!-- 6343   Currency qualifier (C  an..3) -->
				<subelement/>
				<!-- 4405   Status, coded (C  an..3) -->
				<subelement/>
			</element>
		</segment>


	</xsl:template>

	<!-- Invoice lines -->

	<!-- Format and change unit of measure  -->
	<xsl:template name="format_uom">
		<xsl:param name="uom"/>
		<xsl:if test="string($uom)">
			<xsl:choose>
				<xsl:when test="($uom = 'pudel') or ($uom = 'purk') or ($uom = 'tk')">
					<xsl:text>PCE</xsl:text>
				</xsl:when>
				<xsl:otherwise>
					<xsl:value-of select="substring($uom, 1, 3)"/>
				</xsl:otherwise>
			</xsl:choose>
		</xsl:if>
	</xsl:template>
</xsl:stylesheet><!-- Stylus Studio meta-information - (c) 2004-2009. Progress Software Corporation. All rights reserved.

<metaInformation>
	<scenarios>
		<scenario default="yes" name="Scenario1" userelativepaths="yes" externalpreview="no" url="INVOICE_DS041624.xml" htmlbaseurl="" outputurl="" processortype="saxon8" useresolver="yes" profilemode="0" profiledepth="" profilelength="" urlprofilexml=""
		          commandline="" additionalpath="" additionalclasspath="" postprocessortype="none" postprocesscommandline="" postprocessadditionalpath="" postprocessgeneratedext="" validateoutput="no" validator="internal" customvalidator="">
			<advancedProp name="sInitialMode" value=""/>
			<advancedProp name="bXsltOneIsOkay" value="true"/>
			<advancedProp name="bSchemaAware" value="true"/>
			<advancedProp name="bGenerateByteCode" value="true"/>
			<advancedProp name="bXml11" value="false"/>
			<advancedProp name="iValidation" value="0"/>
			<advancedProp name="bExtensions" value="true"/>
			<advancedProp name="iWhitespace" value="0"/>
			<advancedProp name="sInitialTemplate" value=""/>
			<advancedProp name="bTinyTree" value="true"/>
			<advancedProp name="xsltVersion" value="2.0"/>
			<advancedProp name="bWarnings" value="true"/>
			<advancedProp name="bUseDTD" value="false"/>
			<advancedProp name="iErrorHandling" value="fatal"/>
		</scenario>
	</scenarios>
	<MapperMetaTag>
		<MapperInfo srcSchemaPathIsRelative="yes" srcSchemaInterpretAsXML="no" destSchemaPath="" destSchemaRoot="" destSchemaPathIsRelative="yes" destSchemaInterpretAsXML="no"/>
		<MapperBlockPosition></MapperBlockPosition>
		<TemplateContext></TemplateContext>
		<MapperFilter side="source"></MapperFilter>
	</MapperMetaTag>
</metaInformation>
-->