//
//  HFLineCountingRepresenter.m
//  HexFiend_2
//
//  Copyright 2007 ridiculous_fish. All rights reserved.
//

#import <HexFiend/HFLineCountingRepresenter.h>
#import <HexFiend/HFLineCountingView.h>

NSString *const HFLineCountingRepresenterMinimumViewWidthChanged = @"HFLineCountingRepresenterMinimumViewWidthChanged";

/* Returns the maximum advance in points for a hexadecimal digit for the given font (interpreted as a screen font) */
static CGFloat maximumDigitAdvanceForFont(NSFont *font) {
    REQUIRE_NOT_NULL(font);
    font = [font screenFont];
    CGFloat maxDigitAdvance = 0;
    NSDictionary *attributesDictionary = [[NSDictionary alloc] initWithObjectsAndKeys:font, NSFontAttributeName, nil];
    NSTextStorage *storage = [[NSTextStorage alloc] init];
    NSLayoutManager *manager = [[NSLayoutManager alloc] init];
    [storage setFont:font];
    [storage addLayoutManager:manager];
    
    NSSize advancements[16] = {};
    NSGlyph glyphs[16];
    
    /* Generate a glyph for every hex digit */
    for (NSUInteger i=0; i < 16; i++) {
        char c = "0123456789ABCDEF"[i];
        NSString *string = [[NSString alloc] initWithBytes:&c length:1 encoding:NSASCIIStringEncoding];
        [storage replaceCharactersInRange:NSMakeRange(0, (i ? 1 : 0)) withString:string];
        [string release];
        glyphs[i] = [manager glyphAtIndex:0 isValidIndex:NULL];
        HFASSERT(glyphs[i] != NSNullGlyph);
    }
    
    /* Get the advancements of each of those glyphs */
    [font getAdvancements:advancements forGlyphs:glyphs count:sizeof glyphs / sizeof *glyphs];
    
    [manager release];
    [attributesDictionary release];
    [storage release];
    
    /* Find the widest digit */
    for (NSUInteger i=0; i < sizeof glyphs / sizeof *glyphs; i++) {
        maxDigitAdvance = HFMax(maxDigitAdvance, advancements[i].width);
    }
    return maxDigitAdvance;
}

@implementation HFLineCountingRepresenter

- (instancetype)init {
    if ((self = [super init])) {
        minimumDigitCount = 2;
        digitsToRepresentContentsLength = minimumDigitCount;
        interiorShadowEdge = NSMaxXEdge;
        
        _borderedEdges = (1 << NSMaxXEdge);
        _borderColor = [[NSColor controlShadowColor] retain];
        _backgroundColor = [[NSColor windowBackgroundColor] retain];
    }
    return self;
}

- (void)encodeWithCoder:(NSCoder *)coder {
    HFASSERT([coder allowsKeyedCoding]);
    [super encodeWithCoder:coder];
    [coder encodeDouble:lineHeight forKey:@"HFLineHeight"];
    [coder encodeInt64:minimumDigitCount forKey:@"HFMinimumDigitCount"];
    [coder encodeInt64:lineNumberFormat forKey:@"HFLineNumberFormat"];
    [coder encodeObject:self.backgroundColor forKey:@"HFBackgroundColor"];
    [coder encodeObject:self.borderColor forKey:@"HFBorderColor"];
    [coder encodeInt64:self.borderedEdges forKey:@"HFBorderedEdges"];
}

- (instancetype)initWithCoder:(NSCoder *)coder {
    HFASSERT([coder allowsKeyedCoding]);
    self = [super initWithCoder:coder];
    lineHeight = (CGFloat)[coder decodeDoubleForKey:@"HFLineHeight"];
    minimumDigitCount = (NSUInteger)[coder decodeInt64ForKey:@"HFMinimumDigitCount"];
    lineNumberFormat = (HFLineNumberFormat)[coder decodeInt64ForKey:@"HFLineNumberFormat"];
    
    _borderedEdges = [coder decodeObjectForKey:@"HFBorderedEdges"] ? (NSInteger)[coder decodeInt64ForKey:@"HFBorderedEdges"] : 0;
    _borderColor = [[NSColor controlShadowColor] retain];
    _backgroundColor = [[NSColor windowBackgroundColor] retain];

    return self;
}

- (void)dealloc {
    [_borderColor release];
    [_backgroundColor release];
    [super dealloc];
}

- (NSView *)createView {
    HFLineCountingView *result = [[HFLineCountingView alloc] initWithFrame:NSMakeRect(0, 0, 60, 10)];
    [result setRepresenter:self];
    [result setAutoresizingMask:NSViewHeightSizable];
    return result;
}

- (void)postMinimumViewWidthChangedNotification {
    [[NSNotificationCenter defaultCenter] postNotificationName:HFLineCountingRepresenterMinimumViewWidthChanged object:self];
}

- (void)updateDigitAdvanceWithFont:(NSFont *)font {
    CGFloat newDigitAdvance = maximumDigitAdvanceForFont(font);
    if (digitAdvance != newDigitAdvance) {
        digitAdvance = newDigitAdvance;
        [self postMinimumViewWidthChangedNotification];
    }
}

- (void)updateFontAndLineHeight {
    HFLineCountingView *view = [self view];
    HFController *controller = [self controller];
    NSFont *font = controller ? [controller font] : [NSFont fontWithName:HFDEFAULT_FONT size:HFDEFAULT_FONTSIZE];
    [view setFont:font];
    [view setLineHeight: controller ? [controller lineHeight] : HFDEFAULT_FONTSIZE];
    [self updateDigitAdvanceWithFont:font];
}

- (void)updateLineNumberFormat {
    [[self view] setLineNumberFormat:lineNumberFormat];
}

- (void)updateBytesPerLine {
    [[self view] setBytesPerLine:[[self controller] bytesPerLine]];
}

- (void)updateLineRangeToDraw {
    HFFPRange lineRange = {0, 0};
    HFController *controller = [self controller];
    if (controller) {
        lineRange = [controller displayedLineRange];
    }
    [[self view] setLineRangeToDraw:lineRange];
}

- (CGFloat)preferredWidth {
    if (digitAdvance == 0) {
        /* This may happen if we were loaded from a nib.  We are lazy about fetching the controller's font to avoid ordering issues with nib unarchival. */
        [self updateFontAndLineHeight];
    }
    return (CGFloat)10. + digitsToRepresentContentsLength * digitAdvance;
}

- (void)updateMinimumViewWidth {
    HFController *controller = [self controller];
    if (controller) {
        unsigned long long contentsLength = [controller contentsLength];
        NSUInteger bytesPerLine = [controller bytesPerLine];
        /* We want to know how many lines are displayed.  That's equal to the contentsLength divided by bytesPerLine rounded down, except in the case that we're at the end of a line, in which case we need to show one more.  Hence adding 1 and dividing gets us the right result. */
        unsigned long long lineCount = contentsLength / bytesPerLine;
        unsigned long long contentsLengthRoundedToLine = HFProductULL(lineCount, bytesPerLine) - 1;
        NSUInteger digitCount = [HFLineCountingView digitsRequiredToDisplayLineNumber:contentsLengthRoundedToLine inFormat:lineNumberFormat];
        NSUInteger digitWidth = MAX(minimumDigitCount, digitCount);
        if (digitWidth != digitsToRepresentContentsLength) {
            digitsToRepresentContentsLength = digitWidth;
            [self postMinimumViewWidthChangedNotification];
        }
    }
}

- (CGFloat)minimumViewWidthForBytesPerLine:(NSUInteger)bytesPerLine {
    USE(bytesPerLine);
    return [self preferredWidth];
}

- (HFLineNumberFormat)lineNumberFormat {
    return lineNumberFormat;
}

- (void)setLineNumberFormat:(HFLineNumberFormat)format {
    HFASSERT(format < HFLineNumberFormatMAXIMUM);
    lineNumberFormat = format;
    [self updateLineNumberFormat];
    [self updateMinimumViewWidth];
}


- (void)cycleLineNumberFormat {
    lineNumberFormat = (lineNumberFormat + 1) % HFLineNumberFormatMAXIMUM;
    [self updateLineNumberFormat];
    [self updateMinimumViewWidth];
}

- (void)initializeView {
    [self updateFontAndLineHeight];
    [self updateLineNumberFormat];
    [self updateBytesPerLine];
    [self updateLineRangeToDraw];
    [self updateMinimumViewWidth];
}

- (void)controllerDidChange:(HFControllerPropertyBits)bits {
    if (bits & HFControllerDisplayedLineRange) [self updateLineRangeToDraw];
    if (bits & HFControllerBytesPerLine) [self updateBytesPerLine];
    if (bits & (HFControllerFont | HFControllerLineHeight)) [self updateFontAndLineHeight];
    if (bits & (HFControllerContentLength)) [self updateMinimumViewWidth];
}

- (void)setMinimumDigitCount:(NSUInteger)width {
    minimumDigitCount = width;
    [self updateMinimumViewWidth];
}

- (NSUInteger)minimumDigitCount {
    return minimumDigitCount;
}

- (NSUInteger)digitCount {
    return digitsToRepresentContentsLength;
}

+ (NSPoint)defaultLayoutPosition {
    return NSMakePoint(-1, 0);
}

- (void)setInteriorShadowEdge:(NSInteger)edge {
    self->interiorShadowEdge = edge;
    if ([self isViewLoaded]) {
        [[self view] setNeedsDisplay:YES];
    }
}

- (NSInteger)interiorShadowEdge {
    return interiorShadowEdge;
}


- (void)setBorderColor:(NSColor *)color {
    [_borderColor autorelease];
    _borderColor = [color copy];
    if ([self isViewLoaded]) {
        [[self view] setNeedsDisplay:YES];
    }
}

- (void)setBackgroundColor:(NSColor *)color {
    [_backgroundColor autorelease];
    _backgroundColor = [color copy];
    if ([self isViewLoaded]) {
        [[self view] setNeedsDisplay:YES];
    }
}

@end
